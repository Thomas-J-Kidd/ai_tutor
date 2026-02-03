"""
File utilities for the Mistral OCR pipeline.
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from src.models.config import DocumentType
from src.models.results import ProcessingResult

logger = logging.getLogger(__name__)


def find_documents(input_dir: Path, extensions: Optional[List[str]] = None) -> List[Path]:
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


def detect_document_type(file_path: Path) -> DocumentType:
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


def get_image_mime_type(file_path: Path) -> str:
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


def encode_file_to_base64_url(file_path: Path, doc_type: DocumentType) -> str:
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
        DocumentType.IMAGE: get_image_mime_type(file_path)
    }
    mime_type = mime_map.get(doc_type, 'application/octet-stream')
    
    return f"data:{mime_type};base64,{base64_string}"


def create_output_directories(output_dir: Path) -> Dict[str, Path]:
    """
    Create output directory structure
    
    Args:
        output_dir: Base output directory
        
    Returns:
        Dictionary with created directory paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    directories = {
        "base": output_dir,
        "markdown": output_dir / "markdown",
        "json": output_dir / "json",
        "rag": output_dir / "rag_ready",
        "raw": output_dir / "raw_responses",
    }
    
    for dir_path in directories.values():
        dir_path.mkdir(exist_ok=True)
    
    return directories


def save_markdown(result: ProcessingResult, output_dir: Path) -> Path:
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
- **Document Type**: {result.document_type}
- **Processing Time**: {result.processing_time:.2f} seconds
- **Status**: {'Success' if result.successful else 'Failed'}
- **Error**: {result.metadata.error if result.metadata.error else 'None'}
- **Pages**: {result.page_count}
- **Tokens Used**: {result.tokens_used}
- **OCR Model**: {result.metadata.model}

"""
    
    if result.metadata.additional_metadata:
        md_content += "### Additional Metadata\n"
        for key, value in result.metadata.additional_metadata.items():
            if key != "api_response_keys":  # Skip internal keys
                md_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        md_content += "\n"
    
    if result.pages:
        md_content += "## Document Content\n\n"
        
        for page in result.pages:
            md_content += f"### Page {page.page_number}\n\n"
            
            # Add dimensions if available
            if page.dimensions:
                md_content += f"**Dimensions**: {page.dimensions}\n\n"
            
            # Add header if extracted
            if page.header:
                md_content += f"#### Header\n{page.header}\n\n"
            
            # Add main content
            if page.markdown:
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
            if page.footer:
                md_content += f"#### Footer\n{page.footer}\n\n"
            
            # Add tables if available
            if page.tables:
                md_content += "#### Tables\n"
                for j, table in enumerate(page.tables):
                    md_content += f"**Table {j+1}**:\n\n{table}\n\n"
            
            # Add hyperlinks if available
            if page.hyperlinks:
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


def save_json(result: ProcessingResult, output_dir: Path) -> Path:
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
    
    result_dict = result.to_dict()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, indent=2, default=str)
    
    logger.info(f"Saved JSON to: {output_path}")
    return output_path


def create_rag_output(results: List[ProcessingResult], output_dir: Path, 
                     chunk_size: int = 500) -> Optional[Path]:
    """
    Create RAG-ready output from processing results
    
    Args:
        results: List of ProcessingResult objects
        output_dir: Directory to save RAG output
        chunk_size: Target chunk size in characters
        
    Returns:
        Path to RAG output file, or None if no successful results
    """
    successful_results = [r for r in results if r.successful]
    
    if not successful_results:
        return None
    
    output_dir.mkdir(parents=True, exist_ok=True)
    rag_path = output_dir / "slides_chunked.jsonl"
    
    chunks = []
    chunk_id = 0
    
    for result in successful_results:
        for page in result.pages:
            # Extract content
            content = page.markdown or ""
            header = page.header or ""
            footer = page.footer or ""
            
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
                        "page": page.page_number,
                        "chunk_type": "paragraph",
                        "content": para,
                        "metadata": {
                            "document_type": result.document_type,
                            "total_pages": result.page_count,
                            "processing_time": result.processing_time,
                            "ocr_model": result.metadata.model,
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