from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class CrawlRun(Base):
    __tablename__ = "crawl_runs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="in_progress")
    pages_crawled: Mapped[int] = mapped_column(default=0)
    errors: Mapped[int] = mapped_column(default=0)

class Source(Base):
    __tablename__ = "sources"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    source_type: Mapped[str] = mapped_column(String(100))
    
    documents: Mapped[List["Document"]] = relationship(back_populates="source")

class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    title: Mapped[str] = mapped_column(String(512), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(100)) # e.g. "html", "pdf"
    source_domain: Mapped[str] = mapped_column(String(255))
    source_category: Mapped[str] = mapped_column(String(100), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    content_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    source: Mapped[Optional["Source"]] = relationship(back_populates="documents")
    chunks: Mapped[List["Chunk"]] = relationship(back_populates="document")

class Chunk(Base):
    __tablename__ = "chunks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(512), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    section: Mapped[str] = mapped_column(String(255), nullable=True)
    page_number: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    document: Mapped["Document"] = relationship(back_populates="chunks")

class Department(Base):
    __tablename__ = "departments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
