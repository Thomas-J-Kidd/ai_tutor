"""
Result models for the Mistral OCR pipeline.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


@dataclass
class DocumentMetadata:
    """Metadata for a processed document"""
    filename: str
    file_path: Path
    document_type: str
    page_count: int = 0
    processing_time: float = 0.0
    tokens_used: int = 0
    model: str = ""
    attempts: int = 1
    error: Optional[str] = None
    additional_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PageResult:
    """Result for a single page"""
    page_number: int
    dimensions: Optional[Dict[str, float]] = None
    header: Optional[str] = None
    footer: Optional[str] = None
    markdown: Optional[str] = None
    tables: List[str] = field(default_factory=list)
    hyperlinks: List[str] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProcessingResult:
    """Complete processing result for a document"""
    metadata: DocumentMetadata
    pages: List[PageResult] = field(default_factory=list)
    annotations: Optional[Dict[str, Any]] = None
    qna_responses: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def successful(self) -> bool:
        """Check if processing was successful"""
        return self.metadata.error is None
    
    @property
    def filename(self) -> str:
        """Get filename from metadata"""
        return self.metadata.filename
    
    @property
    def file_path(self) -> Path:
        """Get file path from metadata"""
        return self.metadata.file_path
    
    @property
    def document_type(self) -> str:
        """Get document type from metadata"""
        return self.metadata.document_type
    
    @property
    def processing_time(self) -> float:
        """Get processing time from metadata"""
        return self.metadata.processing_time
    
    @property
    def tokens_used(self) -> int:
        """Get tokens used from metadata"""
        return self.metadata.tokens_used
    
    @property
    def page_count(self) -> int:
        """Get page count from metadata"""
        return self.metadata.page_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "metadata": {
                "filename": self.metadata.filename,
                "file_path": str(self.metadata.file_path),
                "document_type": self.metadata.document_type,
                "page_count": self.metadata.page_count,
                "processing_time": self.metadata.processing_time,
                "tokens_used": self.metadata.tokens_used,
                "model": self.metadata.model,
                "attempts": self.metadata.attempts,
                "error": self.metadata.error,
                "additional_metadata": self.metadata.additional_metadata,
            },
            "pages": [
                {
                    "page_number": page.page_number,
                    "dimensions": page.dimensions,
                    "header": page.header,
                    "footer": page.footer,
                    "markdown": page.markdown,
                    "tables": page.tables,
                    "hyperlinks": page.hyperlinks,
                    "images": page.images,
                }
                for page in self.pages
            ],
            "annotations": self.annotations,
            "qna_responses": self.qna_responses,
        }
    
    @classmethod
    def from_api_response(cls, filename: str, file_path: Path, document_type: str, 
                         api_response: Dict[str, Any], processing_time: float, 
                         error: Optional[str] = None) -> "ProcessingResult":
        """
        Create ProcessingResult from API response
        
        Args:
            filename: Name of the file
            file_path: Path to the file
            document_type: Type of document
            api_response: Raw API response
            processing_time: Time taken to process
            error: Optional error message
            
        Returns:
            ProcessingResult object
        """
        metadata = DocumentMetadata(
            filename=filename,
            file_path=file_path,
            document_type=document_type,
            page_count=len(api_response.get("pages", [])),
            processing_time=processing_time,
            tokens_used=api_response.get("usage_info", {}).get("total_tokens", 0),
            model=api_response.get("model", ""),
            error=error,
            additional_metadata={
                "api_response_keys": list(api_response.keys()),
            }
        )
        
        pages = []
        for i, page_data in enumerate(api_response.get("pages", [])):
            page = PageResult(
                page_number=i + 1,
                dimensions=page_data.get("dimensions"),
                header=page_data.get("header"),
                footer=page_data.get("footer"),
                markdown=page_data.get("markdown"),
                tables=page_data.get("tables", []),
                hyperlinks=page_data.get("hyperlinks", []),
                images=page_data.get("images", []),
            )
            pages.append(page)
        
        return cls(
            metadata=metadata,
            pages=pages,
            annotations=api_response.get("document_annotation"),
        )