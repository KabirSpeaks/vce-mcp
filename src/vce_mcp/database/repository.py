from sqlalchemy.orm import Session
from .models import Document, Chunk, Source
from datetime import datetime, timezone
from typing import List, Optional

class VCERepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_document_by_url(self, url: str) -> Optional[Document]:
        return self.db.query(Document).filter(Document.url == url).first()

    def create_or_update_document(self, url: str, title: str, content: str, content_type: str, 
                                  source_domain: str, content_hash: str, category: str = None) -> Document:
        doc = self.get_document_by_url(url)
        if doc:
            doc.title = title
            doc.content = content
            doc.content_hash = content_hash
            doc.updated_at = datetime.now(timezone.utc)
            if category:
                doc.source_category = category
        else:
            doc = Document(
                url=url,
                title=title,
                content=content,
                content_type=content_type,
                source_domain=source_domain,
                source_category=category,
                content_hash=content_hash
            )
            self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc
    
    def add_chunks_for_document(self, document_id: int, chunks_data: List[dict]):
        # Clear old chunks
        self.db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        
        # Add new chunks
        new_chunks = []
        for i, chunk_data in enumerate(chunks_data):
            chunk = Chunk(
                document_id=document_id,
                chunk_index=i,
                title=chunk_data.get('title'),
                content=chunk_data['content'],
                section=chunk_data.get('section'),
                page_number=chunk_data.get('page_number')
            )
            new_chunks.append(chunk)
            self.db.add(chunk)
            
        self.db.commit()
        return new_chunks
