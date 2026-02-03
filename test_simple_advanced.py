#!/usr/bin/env python3
"""
Simple test for the advanced Mistral OCR pipeline.
Tests basic functionality with direct HTTP API calls.
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Import our simple advanced processor
from mistral_ocr_advanced_simple import MistralAdvancedProcessor, BatchProcessor


async def test_basic_functionality():
    """Test basic functionality of the advanced OCR processor"""
    print("=" * 60)
    print("Testing Advanced Mistral OCR Pipeline (Simple Version)")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ MISTRAL_API_KEY not found in .env file")
        return False
    
    print("✓ API key loaded")
    
    # Initialize processor
    try:
        processor = MistralAdvancedProcessor(api_key)
        print("✓ MistralAdvancedProcessor initialized")
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")
        return False
    
    # Check if slides directory exists
    slides_dir = Path(__file__).parent / "slides"
    if not slides_dir.exists():
        print(f"❌ Slides directory not found: {slides_dir}")
        return False
    
    print(f"✓ Slides directory found: {slides_dir}")
    
    # Find PDF files
    pdf_files = list(slides_dir.rglob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in slides directory")
        return False
    
    print(f"✓ Found {len(pdf_files)} PDF files")
    
    # Test with first PDF file
    test_file = pdf_files[0]
    print(f"\nTesting with file: {test_file.name}")
    print(f"File size: {test_file.stat().st_size / 1024:.2f} KB")
    
    try:
        # Test document type detection
        doc_type = processor.detect_document_type(test_file)
        print(f"✓ Document type detected: {doc_type}")
        
        # Test processing with retry
        print("\nTesting OCR processing (this may take a moment)...")
        
        # Modify config for faster testing
        processor.ocr_config.max_retries = 1
        processor.ocr_config.include_image_base64 = False
        
        result = await processor.process_ocr(test_file, processor.ocr_config)
        
        if result.error:
            print(f"❌ Processing failed: {result.error}")
            return False
        
        print(f"✓ Processing successful in {result.processing_time:.2f}s")
        print(f"✓ Pages processed: {result.metadata.get('page_count', 0)}")
        print(f"✓ Tokens used: {result.metadata.get('tokens_used', 0)}")
        
        if result.ocr_response and result.ocr_response.get("pages"):
            print(f"✓ First page content preview:")
            first_page = result.ocr_response["pages"][0]
            if "markdown" in first_page:
                preview = first_page["markdown"][:200] + "..." if len(first_page["markdown"]) > 200 else first_page["markdown"]
                print(f"   {preview}")
        
        # Test Q&A
        print("\nTesting Q&A functionality...")
        qna_response = await processor.ask_question(result, "What is this document about?")
        
        if "error" in qna_response:
            print(f"⚠️ Q&A test warning: {qna_response['error']}")
        else:
            print(f"✓ Q&A successful")
            print(f"   Question: {qna_response.get('question', 'Unknown')}")
            print(f"   Answer preview: {qna_response.get('answer', 'No answer')[:100]}...")
        
        # Test saving to markdown
        print("\nTesting markdown output...")
        test_output_dir = Path(__file__).parent / "test_output_simple"
        test_output_dir.mkdir(exist_ok=True)
        
        md_path = processor.save_to_markdown(result, test_output_dir)
        if md_path.exists():
            print(f"✓ Markdown saved to: {md_path}")
            
            # Show file size
            print(f"   File size: {md_path.stat().st_size / 1024:.2f} KB")
        else:
            print(f"❌ Failed to save markdown")
        
        # Test saving to JSON
        print("\nTesting JSON output...")
        json_path = processor.save_to_json(result, test_output_dir)
        if json_path.exists():
            print(f"✓ JSON saved to: {json_path}")
            print(f"   File size: {json_path.stat().st_size / 1024:.2f} KB")
        else:
            print(f"❌ Failed to save JSON")
        
        # Clean up test output
        import shutil
        if test_output_dir.exists():
            shutil.rmtree(test_output_dir)
            print(f"✓ Cleaned up test output directory")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run test"""
    print("Starting test for Advanced Mistral OCR Pipeline (Simple Version)")
    print("=" * 60)
    
    # Run basic functionality test
    test_passed = await test_basic_functionality()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if test_passed:
        print("✅ Test PASSED! The advanced OCR pipeline is working correctly.")
        print("\nNext steps:")
        print("1. Review the improvements in mistral_ocr_analysis.md")
        print("2. Compare the new mistral_ocr_advanced_simple.py with original mistral_ocr_extractor.py")
        print("3. The new version includes:")
        print("   - Support for annotations (bbox_annotation_format, document_annotation_format)")
        print("   - Document Q&A capabilities")
        print("   - Support for multiple document types (PDF, PPTX, DOCX, images)")
        print("   - Better error handling with retry logic")
        print("   - More comprehensive metadata and output formats")
    else:
        print("❌ Test FAILED. Please check the errors above.")
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()