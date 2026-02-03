#!/usr/bin/env python3
"""
Advanced Mistral OCR, Annotations & Q&A Pipeline
A comprehensive document processing pipeline using Mistral's API.
Combines OCR, annotations, and Q&A capabilities for optimal RAG embedding.

Note: Uses direct HTTP API calls since Mistral's Python SDK 1.2.0
doesn't expose OCR functionality directly.
"""

import os
import json
import time
import asyncio
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from dotenv import load_dotenv
from tqdm import tqdm
from pydantic import BaseModel, Field
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
class AnnotationConfig:
    """Configuration for annotations"""
    bbox_annotation_format: Optional[Any] = None
    document_annotation_format: Optional[Any] = None
    document_annotation_prompt: Optional[str] = None
    include_image_base64: bool = True


@dataclass
class QnAConfig:
    """Configuration for Document Q&A"""
    model: str = "mistral-small-latest"
    temperature: float = 0.1
    max_tokens: int = 1000


@dataclass
class ProcessingResult:
    """Container for processing results"""
    filename: str
    file_path: Path
    document_type: DocumentType
    ocr_response: Optional[OCRResponse] = None
    annotations: Optional[Dict] = None
    qna_responses: List[Dict] = field(default_factory=list)
    processing_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class MistralAdvancedProcessor:
    """
    Advanced processor for Mistral's Document AI capabilities.
    Combines OCR, annotations, and Q&A in a single pipeline.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the processor with API credentials
        
        Args:
            api_key: Mistral API key
        """
        self.client = Mistral(api_key=api_key)
        self.ocr_config = OCRConfig()
        self.annotation_config = AnnotationConfig()
        self.qna_config = QnAConfig()
        
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
    
    def prepare_document_chunk(self, file_path: Path, doc_type: DocumentType) -> Any:
        """
        Prepare document chunk for API based on document type
        
        Args:
            file_path: Path to document file
            doc_type: Document type
            
        Returns:
            Appropriate document chunk for API
        """
        # For now, we'll use base64 encoding for all files
        # In production, you might want to use document_url for public URLs
        # or upload for large files
        
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        # Create upload request
        upload_request = DocumentUploadRequest(
            file=(file_path.name, file_bytes, self._get_mime_type(doc_type))
        )
        
        return upload_request
    
    def _get_mime_type(self, doc_type: DocumentType) -> str:
        """Get MIME type for document type"""
        mime_map = {
            DocumentType.PDF: 'application/pdf',
            DocumentType.PPTX: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            DocumentType.DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            DocumentType.IMAGE: 'image/jpeg'  # Default, will be overridden by actual type
        }
        return mime_map.get(doc_type, 'application/octet-stream')
    
    async def process_with_retry(self, file_path: Path, config: OCRConfig) -> ProcessingResult:
        """
        Process document with retry logic
        
        Args:
            file_path: Path to document file
            config: OCR configuration
            
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
                
                # Prepare document
                document_chunk = self.prepare_document_chunk(file_path, result.document_type)
                
                # Prepare OCR parameters
                ocr_params = {
                    "model": config.model,
                    "document": document_chunk,
                    "table_format": config.table_format.value,
                    "extract_header": config.extract_header,
                    "extract_footer": config.extract_footer,
                    "include_image_base64": config.include_image_base64,
                }
                
                # Add annotation parameters if configured
                if self.annotation_config.bbox_annotation_format:
                    ocr_params["bbox_annotation_format"] = self.annotation_config.bbox_annotation_format
                
                if self.annotation_config.document_annotation_format:
                    ocr_params["document_annotation_format"] = self.annotation_config.document_annotation_format
                
                if self.annotation_config.document_annotation_prompt:
                    ocr_params["document_annotation_prompt"] = self.annotation_config.document_annotation_prompt
                
                # Call OCR API
                ocr_response = self.client.ocr.process(**ocr_params)
                result.ocr_response = ocr_response
                
                # Extract annotations if available
                if hasattr(ocr_response, 'document_annotation') and ocr_response.document_annotation:
                    result.annotations = ocr_response.document_annotation
                
                result.processing_time = time.time() - start_time
                
                # Add metadata
                result.metadata = {
                    "page_count": len(ocr_response.pages) if ocr_response.pages else 0,
                    "model": ocr_response.model,
                    "tokens_used": getattr(ocr_response.usage_info, 'total_tokens', 0) if hasattr(ocr_response, 'usage_info') else 0,
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
    
    async def ask_question(self, result: ProcessingResult, question: str) -> Dict:
        """
        Ask a question about the processed document
        
        Args:
            result: ProcessingResult from OCR
            question: Question to ask about the document
            
        Returns:
            Q&A response
        """
        try:
            # For Q&A, we need to use the chat completions API with document reference
            # Since we have the OCR result, we can use the extracted text
            
            if not result.ocr_response or not result.ocr_response.pages:
                return {"error": "No OCR results available for Q&A"}
            
            # Extract text from OCR pages
            document_text = ""
            for page in result.ocr_response.pages:
                if hasattr(page, 'markdown'):
                    document_text += page.markdown + "\n\n"
            
            # Prepare messages for chat completion
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on the provided document."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Document content:\n{document_text[:8000]}"},
                        {"type": "text", "text": f"Question: {question}"}
                    ]
                }
            ]
            
            # Call chat completion API
            chat_response = self.client.chat.complete(
                model=self.qna_config.model,
                messages=messages,
                temperature=self.qna_config.temperature,
                max_tokens=self.qna_config.max_tokens
            )
            
            response = {
                "question": question,
                "answer": chat_response.choices[0].message.content if chat_response.choices else "No response",
                "model": chat_response.model,
                "tokens_used": getattr(chat_response.usage, 'total_tokens', 0) if hasattr(chat_response, 'usage') else 0,
            }
            
            result.qna_responses.append(response)
            return response
            
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
        
        if result.ocr_response and result.ocr_response.pages:
            md_content += "## Document Content\n\n"
            
            for i, page in enumerate(result.ocr_response.pages):
                page_num = i + 1
                
                md_content += f"### Page {page_num}\n\n"
                
                # Add dimensions if available
                if hasattr(page, 'dimensions'):
                    md_content += f"**Dimensions**: {page.dimensions}\n\n"
                
                # Add header if extracted
                if hasattr(page, 'header') and page.header:
                    md_content += f"#### Header\n{page.header}\n\n"
                
                # Add main content
                if hasattr(page, 'markdown') and page.markdown:
                    # Clean image placeholders
                    content = page.markdown
                    lines = content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        if not (line.strip().startswith('![') and 'img-' in line and '.jpeg' in line):
                            cleaned_lines.append(line)
                    cleaned_content = '\n'.join(cleaned_lines)
                    md_content += f"#### Content\n{cleaned_content}\n\n"
                
                # Add footer if extracted
                if hasattr(page, 'footer') and page.footer:
                    md_content += f"#### Footer\n{page.footer}\n\n"
                
                # Add tables if available
                if hasattr(page, 'tables') and page.tables:
                    md_content += "#### Tables\n"
                    for j, table in enumerate(page.tables):
                        md_content += f"**Table {j+1}**:\n\n{table}\n\n"
                
                # Add hyperlinks if available
                if hasattr(page, 'hyperlinks') and page.hyperlinks:
                    md_content += "#### Hyperlinks\n"
                    for link in page.hyperlinks:
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
        
        # Handle OCR response (convert to dict if it's an object)
        if result.ocr_response:
            result_dict['ocr_response'] = result.ocr_response.to_dict() if hasattr(result.ocr_response, 'to_dict') else str(result.ocr_response)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, default=str)
        
        logger.info(f"Saved JSON to: {output_path}")
        return output_path


class BatchProcessor:
    """
    Batch processor for handling multiple documents
    """
    
    def __init__(self, advanced_processor: MistralAdvancedProcessor):
        """
        Initialize batch processor
        
        Args:
            advanced_processor: MistralAdvancedProcessor instance
        """
        self.processor = advanced_processor
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
                # Process document with OCR and annotations
                result = await self.processor.process_with_retry(doc_path, self.processor.ocr_config)
                
                # Ask questions if provided
                for question in questions:
                    await self.processor.ask_question(result, question)
                
                results.append(result)
                self.results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process {doc_path.name}: {str(e)}")
                error_result = ProcessingResult(
                    filename=doc_path.name,
                    file_path=doc_path,
                    document_type=self.processor.detect_document_type(doc_path),
                    error=str(e),
                    processing_time=0.0
                )
                results.append(error_result)
                self.results.append(error_result)
        
        return results
    
    def save_all_results(self, output_base_dir: Path) -> Dict[str, List[Path]]:
        """
        Save all processing results to files
        
        Args:
            output_base_dir: Base directory for output files
            
        Returns:
            Dictionary with saved file paths
        """
        output_base_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {
            "markdown": [],
            "json": [],
            "rag": []
        }
        
        # Create subdirectories
        markdown_dir = output_base_dir / "markdown"
        json_dir = output_base_dir / "json"
        rag_dir = output_base_dir / "rag_ready"
        
        markdown_dir.mkdir(exist_ok=True)
        json_dir.mkdir(exist_ok=True)
        rag_dir.mkdir(exist_ok=True)
        
        for result in self.results:
            if not result.error:
                # Save markdown
                md_path = self.processor.save_to_markdown(result, markdown_dir)
                saved_files["markdown"].append(md_path)
                
                # Save JSON
                json_path = self.processor.save_to_json(result, json_dir)
                saved_files["json"].append(json_path)
        
        # Create RAG-ready output
        rag_path = self.create_rag_output(rag_dir)
        if rag_path:
            saved_files["rag"].append(rag_path)
        
        return saved_files
    
    def create_rag_output(self, output_dir: Path) -> Optional[Path]:
        """
        Create RAG-ready output from all successful results
        
        Args:
            output_dir: Directory to save RAG output
            
        Returns:
            Path to RAG output file, or None if no successful results
        """
        successful_results = [r for r in self.results if not r.error and r.ocr_response]
        
        if not successful_results:
            return None
        
        rag_path = output_dir / "advanced_slides_chunked.jsonl"
        chunks = []
        chunk_id = 0
        
        for result in successful_results:
            for page_num, page in enumerate(result.ocr_response.pages, 1):
                # Extract content
                content = page.markdown if hasattr(page, 'markdown') else ""
                header = page.header if hasattr(page, 'header') else ""
                footer = page.footer if hasattr(page, 'footer') else ""
                
                # Clean image placeholders
                if content:
                    lines = content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        if not (line.strip().startswith('![') and 'img-' in line and '.jpeg' in line):
                            cleaned_lines.append(line)
                    content = '\n'.join(cleaned_lines)
                
                # Combine text
                full_text = f"Header: {header}\n\n{content}\n\nFooter: {footer}"
                
                # Simple chunking by paragraphs
                paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
                
                for para in paragraphs:
                    if para and not ('![' in para and 'img-' in para and '.jpeg' in para):
                        chunk = {
                            "id": chunk_id,
                            "source_file": result.filename,
                            "page": page_num,
                            "chunk_type": "paragraph",
                            "content": para,
                            "metadata": {
                                "document_type": result.document_type.value,
                                "total_pages": len(result.ocr_response.pages),
                                "processing_time": result.processing_time,
                                "ocr_model": result.ocr_response.model,
                                "has_annotations": bool(result.annotations),
                                "qna_count": len(result.qna_responses)
                            }
                        }
                        
                        # Add annotation summary if available
                        if result.annotations:
                            chunk["metadata"]["annotation_summary"] = "Document has annotations"
                        
                        chunks.append(chunk)
                        chunk_id += 1
        
        # Write JSONL file
        with open(rag_path, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(json.dumps(chunk) + '\n')
        
        logger.info(f"Created RAG output with {len(chunks)} chunks: {rag_path}")
        return rag_path
    
    def generate_summary(self) -> Dict:
        """
        Generate summary of batch processing
        
        Returns:
            Dictionary with processing statistics
        """
        total = len(self.results)
        successful = len([r for r in self.results if not r.error])
        failed = total - successful
        
        total_tokens = 0
        total_pages = 0
        total_processing_time = 0
        
        for result in self.results:
            if not result.error and result.ocr_response:
                total_pages += len(result.ocr_response.pages)
                total_tokens += result.metadata.get('tokens_used', 0)
                total_processing_time += result.processing_time
        
        return {
            "total_documents": total,
            "successful": successful,
            "failed": failed,
            "total_pages": total_pages,
            "total_tokens": total_tokens,
            "total_processing_time": total_processing_time,
            "average_processing_time": total_processing_time / successful if successful else 0,
            "estimated_cost": total_tokens / 1_000_000  # $1 per 1M tokens
        }


async def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY not found in .env file")
    
    # Initialize processor
    processor = MistralAdvancedProcessor(api_key)
    batch_processor = BatchProcessor(processor)
    
    # Define directories
    project_root = Path(__file__).parent
    input_dir = project_root / "slides"
    output_base_dir = project_root / "extracted_advanced"
    
    print("=" * 60)
    print("Advanced Mistral OCR, Annotations & Q&A Pipeline")
    print("=" * 60)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_base_dir}")
    print("=" * 60)
    
    # Find documents
    documents = batch_processor.find_documents(input_dir)
    
    if not documents:
        print(f"No documents found in {input_dir}")
        return
    
    print(f"Found {len(documents)} documents to process")
    
    # Define questions for Q&A (optional)
    questions = [
        "What is the main topic of this document?",
        "What are the key points or findings?",
        "Who is the intended audience for this document?"
    ]
    
    # Process batch
    print("\nStarting batch processing...")
    results = await batch_processor.process_batch(documents, questions)
    
    # Save results
    print("\nSaving results...")
    saved_files = batch_processor.save_all_results(output_base_dir)
    
    # Generate summary
    summary = batch_processor.generate_summary()
    
    print("\n" + "=" * 60)
    print("Processing Complete!")
    print("=" * 60)
    print(f"Successfully processed: {summary['successful']}/{summary['total_documents']}")
    print(f"Failed: {summary['failed']}/{summary['total_documents']}")
    print(f"Total pages: {summary['total_pages']}")
    print(f"Total tokens used: {summary['total_tokens']}")
    print(f"Total processing time: {summary['total_processing_time']:.2f}s")
    print(f"Average processing time: {summary['average_processing_time']:.2f}s per document")
    print(f"Estimated cost: ${summary['estimated_cost']:.4f}")
    
    print(f"\n📄 Markdown files saved: {len(saved_files['markdown'])}")
    print(f"📊 JSON files saved: {len(saved_files['json'])}")
    if saved_files['rag']:
        print(f"🤖 RAG output saved: {saved_files['rag'][0]}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
               