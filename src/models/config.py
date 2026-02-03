"""
Configuration models for the Mistral OCR pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any


class TableFormat(str, Enum):
    """Table format options for OCR"""
    NONE = "null"
    MARKDOWN = "markdown"
    HTML = "html"


class DocumentType(str, Enum):
    """Supported document types"""
    PDF = "pdf"
    PPTX = "pptx"
    DOCX = "docx"
    IMAGE = "image"


@dataclass
class OCRConfig:
    """Configuration for OCR processing"""
    model: str = "mistral-ocr-latest"
    table_format: TableFormat = TableFormat.MARKDOWN
    extract_header: bool = True
    extract_footer: bool = True
    include_image_base64: bool = False
    timeout: int = 120
    max_retries: int = 3
    retry_delay: int = 5


@dataclass
class QnAConfig:
    """Configuration for Document Q&A"""
    enabled: bool = False
    model: str = "mistral-small-latest"
    temperature: float = 0.1
    max_tokens: int = 1000
    questions: List[str] = field(default_factory=lambda: [
        "What is the main topic of this document?",
        "What are the key points or findings?",
        "Who is the intended audience for this document?"
    ])


@dataclass
class AnnotationConfig:
    """Configuration for annotations"""
    enabled: bool = False
    bbox_annotation_format: Optional[Dict[str, Any]] = None
    document_annotation_format: Optional[Dict[str, Any]] = None
    document_annotation_prompt: Optional[str] = None
    include_image_base64: bool = True


@dataclass
class ProcessorConfig:
    """Main processor configuration"""
    processor_type: str = "simple"  # "simple" or "advanced"
    input_dir: Path = field(default_factory=lambda: Path("./slides"))
    output_dir: Path = field(default_factory=lambda: Path("./extracted_text"))
    ocr_config: OCRConfig = field(default_factory=OCRConfig)
    qna_config: QnAConfig = field(default_factory=QnAConfig)
    annotation_config: AnnotationConfig = field(default_factory=AnnotationConfig)
    verbose: bool = False
    quiet: bool = False
    
    def __post_init__(self):
        """Convert string paths to Path objects if needed"""
        if isinstance(self.input_dir, str):
            self.input_dir = Path(self.input_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)