import urllib.robotparser
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class RobotsChecker:
    def __init__(self, user_agent: str = "VCEMCPBot/1.0"):
        self.user_agent = user_agent
        self.parsers = {}
        
    async def _get_parser(self, url: str) -> urllib.robotparser.RobotFileParser:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if base_url not in self.parsers:
            robots_url = f"{base_url}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            try:
                import httpx
                async with httpx.AsyncClient(verify=False) as client:
                    resp = await client.get(robots_url, timeout=5.0)
                    if resp.status_code == 200:
                        lines = resp.text.splitlines()
                        rp.parse(lines)
                        self.parsers[base_url] = rp
                    else:
                        self.parsers[base_url] = None
            except Exception as e:
                logger.warning(f"Could not read robots.txt at {robots_url}: {e}")
                self.parsers[base_url] = None
                
        return self.parsers.get(base_url)

    async def can_fetch(self, url: str) -> bool:
        rp = await self._get_parser(url)
        if rp is None:
            return True # Conservative default? Or True? Let's say True if no robots.txt
        return rp.can_fetch(self.user_agent, url)
