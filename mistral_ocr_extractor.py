#!/usr/bin/env python3
"""
Mistral OCR PDF Text Extractor
Extracts text from PDF slides using Mistral OCR API with direct API implementation.
"""

import os
import base64
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from tqdm import tqdm


@dataclass
class OCRResult:
    """Container for OCR extraction results"""
    filename: str
    pages: List[Dict]
    model: str
    usage_info: Dict
    document_annotation: Optional[Dict]
    processing_time: float
    page_count: int


class MistralOCRExtractor:
    """Handles OCR extraction using Mistral Direct API"""
    
    def __init__(self, api_key: str):
        """
        Initialize the OCR extractor with API credentials
        
        Args:
            api_key: Mistral API key
        """
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def encode_pdf_to_base64_url(self, pdf_path: Path) -> str:
        """
        Encode PDF file to base64 data URL
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Data URL string: "data:application/pdf;base64,{base64_string}"
        """
        with open(pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        base64_string = base64.b64encode(pdf_bytes).decode('utf-8')
        return f"data:application/pdf;base64,{base64_string}"
    
    def extract_text_from_pdf(self, pdf_path: Path) -> OCRResult:
        """
        Extract text from a PDF using Mistral OCR API
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            OCRResult object containing extracted text and metadata
            
        Raises:
            Exception: If API call fails
        """
        start_time = time.time()
        
        # Encode PDF to base64 data URL
        data_url = self.encode_pdf_to_base64_url(pdf_path)
        
        try:
            # Prepare API request payload
            payload = {
                "model": "mistral-ocr-latest",
                "document": {
                    "type": "document_url",
                    "document_url": data_url
                },
                "table_format": "markdown",
                "extract_header": True,
                "extract_footer": True,
                "include_image_base64": False
            }
            
            # Make API request using direct HTTP
            response = requests.post(
                f"{self.base_url}/ocr",
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                raise Exception(f"API error {response.status_code}: {response.text}")
            
            processing_time = time.time() - start_time
            response_dict = response.json()
            
            return OCRResult(
                filename=pdf_path.name,
                pages=response_dict.get("pages", []),
                model=response_dict.get("model", ""),
                usage_info=response_dict.get("usage_info", {}),
                document_annotation=response_dict.get("document_annotation"),
                processing_time=processing_time,
                page_count=len(response_dict.get("pages", []))
            )
            
        except Exception as e:
            raise Exception(f"Mistral OCR API error: {str(e)}")
    
    def save_to_markdown(self, result: OCRResult, output_dir: Path) -> Path:
        """
        Save OCR result to markdown file with structured format
        
        Args:
            result: OCRResult object
            output_dir: Directory to save markdown file
            
        Returns:
            Path to saved markdown file
        """
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename (same as PDF but with .md extension)
        md_filename = result.filename.replace('.pdf', '.md')
        output_path = output_dir / md_filename
        
        # Create markdown content
        md_content = f"""# {result.filename}

## Metadata
- **Total Pages**: {result.page_count}
- **OCR Model**: {result.model}
- **Processing Time**: {result.processing_time:.2f} seconds
- **Source File**: {result.filename}
- **Tokens Used**: {result.usage_info.get('total_tokens', 'N/A')}

## Document Structure

"""
        
        # Process each page
        for page in result.pages:
            page_num = page.get("index", 0) + 1  # Convert 0-index to 1-index
            
            md_content += f"""### Page {page_num}

**Dimensions**: {page.get('dimensions', {})}

#### Header
{page.get('header', 'No header extracted')}

#### Main Content
"""
            
            # Get markdown content and remove image placeholders
            markdown_content = page.get('markdown', 'No content extracted')
            # Remove image placeholders (lines containing ![img-*.jpeg](img-*.jpeg))
            lines = markdown_content.split('\n')
            cleaned_lines = []
            for line in lines:
                # Skip lines that are image placeholders
                if not (line.strip().startswith('![') and 'img-' in line and '.jpeg' in line):
                    cleaned_lines.append(line)
            
            cleaned_markdown = '\n'.join(cleaned_lines)
            md_content += f"{cleaned_markdown}\n\n"
            
            md_content += f"""#### Footer
{page.get('footer', 'No footer extracted')}

#### Tables
"""
            
            tables = page.get("tables", [])
            if tables:
                for i, table in enumerate(tables):
                    md_content += f"**Table {i+1}**:\n\n{table}\n\n"
            else:
                md_content += "No tables extracted\n"
            
            md_content += "#### Hyperlinks\n"
            hyperlinks = page.get("hyperlinks", [])
            if hyperlinks:
                for link in hyperlinks:
                    md_content += f"- {link}\n"
            else:
                md_content += "No hyperlinks detected\n"
            
            md_content += "\n---\n\n"
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return output_path
    
    def save_raw_response(self, result: OCRResult, output_dir: Path) -> Path:
        """
        Save raw API response as JSON for debugging
        
        Args:
            result: OCRResult object
            output_dir: Directory to save JSON file
            
        Returns:
            Path to saved JSON file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        json_filename = result.filename.replace('.pdf', '_raw.json')
        output_path = output_dir / json_filename
        
        result_dict = {
            "filename": result.filename,
            "model": result.model,
            "page_count": result.page_count,
            "processing_time": result.processing_time,
            "usage_info": result.usage_info,
            "document_annotation": result.document_annotation,
            "pages": result.pages
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, default=str)
        
        return output_path


class SlideProcessor:
    """Processes slides directory and manages OCR extraction"""
    
    def __init__(self, extractor: MistralOCRExtractor):
        """
        Initialize slide processor
        
        Args:
            extractor: MistralOCRExtractor instance
        """
        self.extractor = extractor
        self.results: List[OCRResult] = []
        
    def find_pdf_files(self, slides_dir: Path) -> List[Path]:
        """
        Recursively find all PDF files in directory
        
        Args:
            slides_dir: Root directory containing slides
            
        Returns:
            List of Path objects to PDF files
        """
        pdf_files = []
        for ext in ['*.pdf', '*.PDF']:
            pdf_files.extend(slides_dir.rglob(ext))
        return sorted(pdf_files)
    
    def process_directory(self, slides_dir: Path, output_base_dir: Path) -> Dict:
        """
        Process all PDF files in directory and subdirectories
        
        Args:
            slides_dir: Root directory containing slides
            output_base_dir: Base directory for output files
            
        Returns:
            Dictionary with processing statistics
        """
        # Find all PDF files
        pdf_files = self.find_pdf_files(slides_dir)
        
        if not pdf_files:
            print(f"No PDF files found in {slides_dir}")
            return {"processed": 0, "failed": 0, "total": 0}
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        # Create raw responses directory
        raw_dir = output_base_dir / "raw_responses"
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each PDF file
        successful = 0
        failed = 0
        
        for pdf_path in tqdm(pdf_files, desc="Processing PDFs with Mistral OCR"):
            try:
                # Determine output directory structure
                relative_path = pdf_path.relative_to(slides_dir)
                output_dir = output_base_dir / relative_path.parent
                
                # Extract text using OCR
                print(f"\n📄 Processing: {pdf_path.name}")
                print(f"   Size: {pdf_path.stat().st_size / 1024 / 1024:.2f} MB")
                
                result = self.extractor.extract_text_from_pdf(pdf_path)
                self.results.append(result)
                
                # Save to markdown
                md_path = self.extractor.save_to_markdown(result, output_dir)
                print(f"  ✓ Saved markdown to: {md_path}")
                
                # Save raw response for debugging
                json_path = self.extractor.save_raw_response(result, raw_dir / relative_path.parent)
                print(f"  ✓ Saved raw response to: {json_path}")
                
                print(f"  ✓ Pages: {result.page_count}")
                print(f"  ✓ Tokens used: {result.usage_info.get('total_tokens', 'N/A')}")
                
                successful += 1
                
            except Exception as e:
                print(f"\n✗ Failed to process {pdf_path.name}: {str(e)}")
                failed += 1
        
        return {
            "processed": successful,
            "failed": failed,
            "total": len(pdf_files)
        }
    
    def create_consolidated_output(self, output_dir: Path) -> Path:
        """
        Create a consolidated markdown file with all extracted text
        
        Args:
            output_dir: Directory to save consolidated file
            
        Returns:
            Path to consolidated file
        """
        if not self.results:
            raise ValueError("No results to consolidate")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        consolidated_path = output_dir / "all_slides_consolidated.md"
        
        md_content = "# Consolidated Slide Text\n\n"
        md_content += f"*Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n"
        md_content += f"*Total Files: {len(self.results)}*\n\n"
        
        total_tokens = 0
        total_pages = 0
        
        for result in self.results:
            total_tokens += result.usage_info.get('total_tokens', 0)
            total_pages += result.page_count
            
            md_content += f"""## {result.filename}

**Pages**: {result.page_count} | **Processing Time**: {result.processing_time:.2f}s | **Tokens**: {result.usage_info.get('total_tokens', 'N/A')}

### Content Summary

"""
            
            # Add first page preview
            if result.pages:
                first_page = result.pages[0]
                preview = first_page.get('markdown', '')[:500]
                if len(first_page.get('markdown', '')) > 500:
                    preview += "..."
                md_content += f"{preview}\n\n"
            
            md_content += f"[View full extraction](./{result.filename.replace('.pdf', '.md')})\n\n"
            md_content += "---\n\n"
        
        md_content += f"\n## Summary\n"
        md_content += f"- **Total Files Processed**: {len(self.results)}\n"
        md_content += f"- **Total Pages**: {total_pages}\n"
        md_content += f"- **Total Tokens Used**: {total_tokens}\n"
        md_content += f"- **OCR Model**: {self.results[0].model if self.results else 'N/A'}\n"
        
        with open(consolidated_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return consolidated_path
    
    def create_rag_ready_output(self, output_dir: Path) -> Path:
        """
        Create a RAG-ready output with chunked content
        
        Args:
            output_dir: Directory to save RAG-ready file
            
        Returns:
            Path to RAG-ready file
        """
        if not self.results:
            raise ValueError("No results to process")
        
        rag_dir = output_dir / "rag_ready"
        rag_dir.mkdir(parents=True, exist_ok=True)
        
        rag_path = rag_dir / "slides_chunked.jsonl"
        
        chunks = []
        chunk_id = 0
        
        for result in self.results:
            for page_num, page in enumerate(result.pages, 1):
                # Create chunks from page content
                content = page.get('markdown', '')
                header = page.get('header', '')
                footer = page.get('footer', '')
                
                # Remove image placeholders from content
                if content:
                    lines = content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        # Skip lines that are image placeholders
                        if not (line.strip().startswith('![') and 'img-' in line and '.jpeg' in line):
                            cleaned_lines.append(line)
                    content = '\n'.join(cleaned_lines)
                
                # Combine all text
                full_text = f"Header: {header}\n\n{content}\n\nFooter: {footer}"
                
                # Simple chunking by paragraphs (split by double newlines)
                paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
                
                for para in paragraphs:
                    if para:  # Skip empty paragraphs
                        # Also clean each paragraph individually
                        if '![' in para and 'img-' in para and '.jpeg' in para:
                            # Skip paragraphs that are just image placeholders
                            continue
                            
                        chunk = {
                            "id": chunk_id,
                            "source_file": result.filename,
                            "page": page_num,
                            "chunk_type": "paragraph",
                            "content": para,
                            "metadata": {
                                "total_pages": result.page_count,
                                "processing_time": result.processing_time,
                                "ocr_model": result.model
                            }
                        }
                        chunks.append(chunk)
                        chunk_id += 1
        
        # Write as JSONL (one JSON object per line)
        with open(rag_path, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                f.write(json.dumps(chunk) + '\n')
        
        return rag_path


def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("MISTAL_API_KEY")
    if not api_key:
        raise ValueError("MISTAL_API_KEY not found in .env file")
    
    # Initialize extractor and processor
    extractor = MistralOCRExtractor(api_key)
    processor = SlideProcessor(extractor)
    
    # Define directories
    project_root = Path(__file__).parent
    slides_dir = project_root / "slides"
    output_base_dir = project_root / "extracted_text"
    
    print("=" * 60)
    print("Mistral OCR PDF Text Extractor")
    print("=" * 60)
    print(f"Slides directory: {slides_dir}")
    print(f"Output directory: {output_base_dir}")
    print(f"API Key: {'*' * 20}{api_key[-4:] if api_key else 'NOT FOUND'}")
    print("=" * 60)
    
    # Process all PDF files
    stats = processor.process_directory(slides_dir, output_base_dir)
    
    print("\n" + "=" * 60)
    print("Processing Complete!")
    print("=" * 60)
    print(f"Successfully processed: {stats['processed']}/{stats['total']}")
    print(f"Failed: {stats['failed']}/{stats['total']}")
    
    if stats['processed'] > 0:
        # Create consolidated output
        try:
            consolidated_path = processor.create_consolidated_output(output_base_dir)
            print(f"\n📄 Consolidated file created: {consolidated_path}")
        except Exception as e:
            print(f"\nNote: Could not create consolidated file: {e}")
        
        # Create RAG-ready output
        try:
            rag_path = processor.create_rag_ready_output(output_base_dir)
            print(f"🤖 RAG-ready file created: {rag_path}")
            print(f"   Contains {len(processor.results)} files, chunked for vector database")
        except Exception as e:
            print(f"Note: Could not create RAG-ready file: {e}")
        
        # Print summary
        print("\n📊 Summary of processed files:")
        total_tokens = 0
        for result in processor.results:
            tokens = result.usage_info.get('total_tokens', 0)
            total_tokens += tokens
            print(f"  • {result.filename}: {result.page_count} pages, {tokens} tokens")
        
        print(f"\n💰 Estimated cost (approx): ${total_tokens / 1_000_000:.4f}")
        print("   (Based on Mistral OCR pricing: $1 per 1M tokens)")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()