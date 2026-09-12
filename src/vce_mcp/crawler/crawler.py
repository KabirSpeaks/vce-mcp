import httpx
import logging
import hashlib
from urllib.parse import urlparse
import time
from typing import Set, Dict, List
import yaml
from sqlalchemy.orm import Session
import os

from .robots import RobotsChecker
from .parser import parse_html
from .pdf_parser import parse_pdf
from ..database.repository import VCERepository
from ..database.models import CrawlRun
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class VCECrawler:
    def __init__(self, db: Session, max_depth: int = 3, max_pages: int = 200):
        self.db = db
        self.repo = VCERepository(db)
        self.robots = RobotsChecker()
        self.max_depth = max_depth
        self.max_pages = max_pages
        
        self.visited_urls: Set[str] = set()
        self.pages_crawled = 0
        self.errors = 0
        
        self.config = self._load_config()
        self.allowed_domains = set()
        self.excluded_paths = set()
        
        for source in self.config.get('sources', []):
            if 'allowed_domains' in source:
                self.allowed_domains.update(source['allowed_domains'])
            if 'excluded_paths' in source:
                self.excluded_paths.update(source['excluded_paths'])

    def _load_config(self) -> dict:
        config_path = os.path.join(os.path.dirname(__file__), '../../../config/sources.yaml')
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading sources config: {e}")
            return {'sources': []}

    def is_allowed_url(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Check domain
        if not any(domain == d or domain.endswith('.' + d) for d in self.allowed_domains):
            return False
            
        # Check excluded paths
        if any(parsed.path.startswith(ex) for ex in self.excluded_paths):
            return False
            
        # Check extensions to ignore (images, etc)
        ignored_extensions = ['.jpg', '.png', '.gif', '.zip', '.rar', '.mp4']
        if any(parsed.path.lower().endswith(ext) for ext in ignored_extensions):
            return False
            
        return True

    def get_content_hash(self, content_bytes: bytes) -> str:
        return hashlib.sha256(content_bytes).hexdigest()

    async def fetch(self, url: str) -> tuple[httpx.Response, bytes]:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response, response.content

    async def process_url(self, url: str, depth: int) -> Set[str]:
        if depth > self.max_depth or self.pages_crawled >= self.max_pages:
            return set()
            
        if url in self.visited_urls:
            return set()
            
        if not self.is_allowed_url(url):
            return set()
            
        if not await self.robots.can_fetch(url):
            logger.info(f"Robots.txt restricted: {url}")
            return set()

        self.visited_urls.add(url)
        logger.info(f"Crawling ({depth}/{self.max_depth}) [{self.pages_crawled}/{self.max_pages}]: {url}")
        
        try:
            response, content_bytes = await self.fetch(url)
            self.pages_crawled += 1
            
            content_hash = self.get_content_hash(content_bytes)
            content_type = response.headers.get('Content-Type', '').lower()
            parsed_url = urlparse(url)
            
            existing_doc = self.repo.get_document_by_url(url)
            if existing_doc and existing_doc.content_hash == content_hash:
                logger.info(f"Content unchanged: {url}")
                # We still might want to extract links from it if it's HTML?
                # But for simplicity, we can skip if unchanged. 
                # Let's re-parse for links just to continue crawl, or assume links are already visited.
                pass 
                
            links = set()
            
            if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
                text, chunks = parse_pdf(content_bytes)
                doc = self.repo.create_or_update_document(
                    url=url, title=f"PDF Document: {url.split('/')[-1]}",
                    content=text, content_type='pdf', source_domain=parsed_url.netloc,
                    content_hash=content_hash
                )
                self.repo.add_chunks_for_document(doc.id, chunks)
                
            elif 'text/html' in content_type:
                html = content_bytes.decode('utf-8', errors='ignore')
                title, text, links, chunks = parse_html(html, url)
                doc = self.repo.create_or_update_document(
                    url=url, title=title, content=text, content_type='html',
                    source_domain=parsed_url.netloc, content_hash=content_hash
                )
                self.repo.add_chunks_for_document(doc.id, chunks)
            
            time.sleep(0.5) # rate limiting
            
            # Filter links to follow
            valid_links = {l for l in links if self.is_allowed_url(l) and l not in self.visited_urls}
            return valid_links
            
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            self.errors += 1
            return set()

    async def run(self):
        run_record = CrawlRun(status="in_progress")
        self.db.add(run_record)
        self.db.commit()
        
        queue = []
        for source in self.config.get('sources', []):
            queue.append((source['url'], 0))
            
        try:
            while queue and self.pages_crawled < self.max_pages:
                url, depth = queue.pop(0)
                new_links = await self.process_url(url, depth)
                for link in new_links:
                    queue.append((link, depth + 1))
                    
            run_record.status = "completed"
        except Exception as e:
            logger.error(f"Crawl aborted: {e}")
            run_record.status = "failed"
            
        run_record.completed_at = datetime.now(timezone.utc)
        run_record.pages_crawled = self.pages_crawled
        run_record.errors = self.errors
        self.db.commit()
        logger.info(f"Crawl finished. Pages: {self.pages_crawled}, Errors: {self.errors}")
