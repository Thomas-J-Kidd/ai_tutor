#!/usr/bin/env python3
"""
Advanced Mistral OCR Pipeline - Simplified Version
Uses direct HTTP API calls to access OCR, annotations, and Q&A features.
Based on documentation analysis and working mistral_ocr_extractor.py
"""

import os
import json
import time
import base64
import asyncio
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from dotenv import load_dotenv
from tqdm import tqdm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
class ProcessingResult:
    """Container for processing results"""
    filename: str
    file_path: Path
    document_type: DocumentType
    ocr_response: Optional[Dict] = None
    annotations: Optional[Dict] = None
    qna_responses: List[Dict] = field(default_factory=list)
    processing_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class MistralAdvancedProcessor:
    """
    Advanced processor for Mistral's Document AI capabilities.
    Uses direct HTTP API calls for OCR, annotations, and Q&A.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the processor with API credentials
        
        Args:
            api_key: Mistral API key
        """
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.ocr_config = OCRConfig()
        
    def detect_document_type(self, file_path: Path) -> DocumentType:
        """
        Detect document type from file extension
        
        Args:
            file_path: Path to document file
            
        Returns:
            DocumentType enum
        """
        ext = file_path.suffix.lower()
        if ext == '.pdf':
            return DocumentType.PDF
        elif ext in ['.pptx', '.ppt']:
            return DocumentType.PPTX
        elif ext in ['.docx', '.doc']:
            return DocumentType.DOCX
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.avif']:
            return DocumentType.IMAGE
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def encode_file_to_base64_url(self, file_path: Path, doc_type: DocumentType) -> str:
        """
        Encode file to base64 data URL
        
        Args:
            file_path: Path to file
            doc_type: Document type
            
        Returns:
            Data URL string
        """
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        base64_string = base64.b64encode(file_bytes).decode('utf-8')
        
        # Determine MIME type
        mime_map = {
            DocumentType.PDF: 'application/pdf',
            DocumentType.PPTX: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            DocumentType.DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            DocumentType.IMAGE: self._get_image_mime_type(file_path)
        }
        mime_type = mime_map.get(doc_type, 'application/octet-stream')
        
        return f"data:{mime_type};base64,{base64_string}"
    
    def _get_image_mime_type(self, file_path: Path) -> str:
        """Get MIME type for image file"""
        ext = file_path.suffix.lower()
        mime_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.webp': 'image/webp',
            '.avif': 'image/avif',
        }
        return mime_map.get(ext, 'image/jpeg')
    
    async def process_ocr(self, file_path: Path, config: OCRConfig, 
                         bbox_annotation_format: Optional[Dict] = None,
                         document_annotation_format: Optional[Dict] = None,
                         document_annotation_prompt: Optional[str] = None) -> ProcessingResult:
        """
        Process document with OCR and optional annotations
        
        Args:
            file_path: Path to document file
            config: OCR configuration
            bbox_annotation_format: Optional bbox annotation format
            document_annotation_format: Optional document annotation format
            document_annotation_prompt: Optional annotation prompt
            
        Returns:
            ProcessingResult object
        """
        start_time = time.time()
        result = ProcessingResult(
            filename=file_path.name,
            file_path=file_path,
            document_type=self.detect_document_type(file_path)
        )
        
        for attempt in range(config.max_retries):
            try:
                logger.info(f"Processing {file_path.name} (attempt {attempt + 1}/{config.max_retries})")
                
                # Encode file to base64 URL
                data_url = self.encode_file_to_base64_url(file_path, result.document_type)
                
                # Determine document type for API
                if result.document_type == DocumentType.IMAGE:
                    document_field = {
                        "type": "image_url",
                        "image_url": data_url
                    }
                else:
                    document_field = {
                        "type": "document_url",
                        "document_url": data_url
                    }
                
                # Prepare OCR request payload
                payload = {
                    "model": config.model,
                    "document": document_field,
                    "table_format": config.table_format.value,
                    "extract_header": config.extract_header,
                    "extract_footer": config.extract_footer,
                    "include_image_base64": config.include_image_base64,
                }
                
                # Add annotation parameters if provided
                if bbox_annotation_format:
                    payload["bbox_annotation_format"] = bbox_annotation_format
                
                if document_annotation_format:
                    payload["document_annotation_format"] = document_annotation_format
                
                if document_annotation_prompt:
                    payload["document_annotation_prompt"] = document_annotation_prompt
                
                # Make API request
                response = requests.post(
                    f"{self.base_url}/ocr",
                    headers=self.headers,
                    json=payload,
                    timeout=config.timeout
                )
                
                if response.status_code != 200:
                    raise Exception(f"API error {response.status_code}: {response.text}")
                
                response_dict = response.json()
                result.ocr_response = response_dict
                
                # Extract annotations if available
                if "document_annotation" in response_dict and response_dict["document_annotation"]:
                    result.annotations = response_dict["document_annotation"]
                
                result.processing_time = time.time() - start_time
                
                # Add metadata
                result.metadata = {
                    "page_count": len(response_dict.get("pages", [])),
                    "model": response_dict.get("model", ""),
                    "tokens_used": response_dict.get("usage_info", {}).get("total_tokens", 0),
                    "attempts": attempt + 1,
                }
                
                logger.info(f"Successfully processed {file_path.name} in {result.processing_time:.2f}s")
                return result
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {file_path.name}: {str(e)}")
                if attempt < config.max_retries - 1:
                    await asyncio.sleep(config.retry_delay)
                else:
                    result.error = str(e)
                    result.processing_time = time.time() - start_time
        
        return result
    
    async def ask_question(self, result: ProcessingResult, question: str, 
                          model: str = "mistral-small-latest") -> Dict:
        """
        Ask a question about the processed document using chat completions
        
        Args:
            result: ProcessingResult from OCR
            question: Question to ask about the document
            model: Model to use for Q&A
            
        Returns:
            Q&A response
        """
        try:
            if not result.ocr_response or not result.ocr_response.get("pages"):
                return {"error": "No OCR results available for Q&A"}
            
            # Extract text from OCR pages
            document_text = ""
            for page in result.ocr_response.get("pages", []):
                document_text += page.get("markdown", "") + "\n\n"
            
            # Prepare chat completion request
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Document content:\n{document_text[:8000]}"},
                        {"type": "text", "text": f"Question: {question}"}
                    ]
                }
            ]
            
            chat_payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=chat_payload,
                timeout=120
            )
            
            if response.status_code != 200:
                return {"error": f"Chat API error {response.status_code}: {response.text}"}
            
            chat_response = response.json()
            
            qna_response = {
                "question": question,
                "answer": chat_response["choices"][0]["message"]["content"] if chat_response.get("choices") else "No response",
                "model": chat_response.get("model", model),
                "tokens_used": chat_response.get("usage", {}).get("total_tokens", 0),
            }
            
            result.qna_responses.append(qna_response)
            return qna_response
            
        except Exception as e:
            logger.error(f"Q&A failed for {result.filename}: {str(e)}")
            return {"error": str(e), "question": question}
    
    def save_to_markdown(self, result: ProcessingResult, output_dir: Path) -> Path:
        """
        Save processing result to markdown file
        
        Args:
            result: ProcessingResult object
            output_dir: Directory to save markdown file
            
        Returns:
            Path to saved markdown file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        md_filename = result.filename.rsplit('.', 1)[0] + '.md'
        output_path = output_dir / md_filename
        
        md_content = f"""# {result.filename}

## Metadata
- **Document Type**: {result.document_type.value}
- **Processing Time**: {result.processing_time:.2f} seconds
- **Status**: {'Success' if not result.error else 'Failed'}
- **Error**: {result.error if result.error else 'None'}

"""
        
        if result.metadata:
            md_content += "### Processing Metadata\n"
            for key, value in result.metadata.items():
                md_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
            md_content += "\n"
        
        if result.ocr_response and result.ocr_response.get("pages"):
            md_content += "## Document Content\n\n"
            
            for i, page in enumerate(result.ocr_response.get("pages", [])):
                page_num = i + 1
                
                md_content += f"### Page {page_num}\n\n"
                
                # Add dimensions if available
                if "dimensions" in page:
                    md_content += f"**Dimensions**: {page['dimensions']}\n\n"
                
                # Add header if extracted
                if "header" in page and page["header"]:
                    md_content += f"#### Header\n{page['header']}\n\n"
                
                # Add main content
                if "markdown" in page and page["markdown"]:
                    # Clean image placeholders
                    content = page["markdown"]
                    lines = content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        if not (line.strip().startswith('![') and 'img-' in line and '.jpeg' in line):
                            cleaned_lines.append(line)
                    cleaned_content = '\n'.join(cleaned_lines)
                    md_content += f"#### Content\n{cleaned_content}\n\n"
                
                # Add footer if extracted
                if "footer" in page and page["footer"]:
                    md_content += f"#### Footer\n{page['footer']}\n\n"
                
                # Add tables if available
                if "tables" in page and page["tables"]:
                    md_content += "#### Tables\n"
                    for j, table in enumerate(page["tables"]):
                        md_content += f"**Table {j+1}**:\n\n{table}\n\n"
                
                # Add hyperlinks if available
                if "hyperlinks" in page and page["hyperlinks"]:
                    md_content += "#### Hyperlinks\n"
                    for link in page["hyperlinks"]:
                        md_content += f"- {link}\n"
                    md_content += "\n"
                
                md_content += "---\n\n"
        
        if result.annotations:
            md_content += "## Annotations\n\n"
            md_content += f"```json\n{json.dumps(result.annotations, indent=2)}\n```\n\n"
        
        if result.qna_responses:
            md_content += "## Question & Answers\n\n"
            for qna in result.qna_responses:
                md_content += f"### Q: {qna.get('question', 'Unknown')}\n"
                md_content += f"**A**: {qna.get('answer', 'No answer')}\n\n"
                if 'model' in qna:
                    md_content += f"*Model: {qna['model']}, Tokens: {qna.get('tokens_used', 'N/A')}*\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Saved markdown to: {output_path}")
        return output_path
    
    def save_to_json(self, result: ProcessingResult, output_dir: Path) -> Path:
        """
        Save processing result to JSON file
        
        Args:
            result: ProcessingResult object
            output_dir: Directory to save JSON file
            
        Returns:
            Path to saved JSON file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        json_filename = result.filename.rsplit('.', 1)[0] + '_full.json'
        output_path = output_dir / json_filename
        
        # Convert result to dict
        result_dict = asdict(result)
        
        # Handle Path objects
        result_dict['file_path'] = str(result_dict['file_path'])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, default=str)
        
        logger.info(f"Saved JSON to: {output_path}")
        return output_path


class BatchProcessor:
    """
    Batch processor for handling multiple documents
    """
    
    def __init__(self, processor: MistralAdvancedProcessor):
        """
        Initialize batch processor
        
        Args:
            processor: MistralAdvancedProcessor instance
        """
        self.processor = processor
        self.results: List[ProcessingResult] = []
    
    def find_documents(self, input_dir: Path, extensions: List[str] = None) -> List[Path]:
        """
        Find documents in directory
        
        Args:
            input_dir: Directory to search
            extensions: List of file extensions to include
            
        Returns:
            List of document paths
        """
        if extensions is None:
            extensions = ['.pdf', '.pptx', '.docx', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
        
        documents = []
        for ext in extensions:
            documents.extend(input_dir.rglob(f'*{ext}'))
            documents.extend(input_dir.rglob(f'*{ext.upper()}'))
        
        return sorted(documents)
    
    async def process_batch(self, documents: List[Path], questions: List[str] = None) -> List[ProcessingResult]:
        """
        Process batch of documents
        
        Args:
            documents: List of document paths
            questions: Optional list of questions to ask for Q&A
            
        Returns:
            List of ProcessingResult objects
        """
        if questions is None:
            questions = []
        
        results = []
        
        for doc_path in tqdm(documents, desc="Processing documents"):
            try:
                # Process document with OCR
                result = await self.processor.process_ocr(doc_path, self.processor.ocr_config)
                
                # Ask questions if provided
                for question in questions:
                    await self.processor.ask_question(result, question)
                
                results.append(result)
                self.results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process {doc_path.name}: {str(e)}")
