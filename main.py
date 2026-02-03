#!/usr/bin/env python3
"""
Mistral OCR Pipeline - Main Entry Point
Command-line interface for extracting text from documents using Mistral OCR API.
Supports both simple and advanced processors with configurable options.
"""

import os
import sys
import asyncio
import argparse
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.processors.simple_processor import SimpleProcessor
from src.processors.advanced_processor import AdvancedProcessor
from src.utils.logging_utils import setup_logging
from src.models.config import ProcessorConfig, OCRConfig, QnAConfig, AnnotationConfig


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Dictionary with configuration
    """
    default_config = {
        "processor": {
            "type": "simple",
            "input_dir": "./slides",
            "output_dir": "./extracted_text",
            "max_retries": 3,
            "retry_delay": 5,
        },
        "ocr": {
            "model": "mistral-ocr-latest",
            "table_format": "markdown",
            "extract_header": True,
            "extract_footer": True,
            "include_image_base64": False,
            "timeout": 120,
        },
        "qna": {
            "enabled": False,
            "model": "mistral-small-latest",
            "temperature": 0.1,
            "max_tokens": 1000,
            "questions": [
                "What is the main topic of this document?",
                "What are the key points or findings?",
                "Who is the intended audience for this document?"
            ]
        },
        "annotations": {
            "enabled": False,
            "bbox_annotation_format": None,
            "document_annotation_format": None,
            "document_annotation_prompt": None,
            "include_image_base64": True,
        }
    }
    
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                # Merge with defaults (file config overrides defaults)
                if file_config:
                    for key in default_config:
                        if key in file_config:
                            default_config[key].update(file_config[key])
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
    
    return default_config


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Extract text from documents using Mistral OCR API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default settings
  python main.py
  
  # Specify input directory
  python main.py --input-dir ./my_slides
  
  # Use advanced processor
  python main.py --processor advanced
  
  # Specify output directory
  python main.py --output-dir ./my_output
  
  # Use config file
  python main.py --config config.yaml
  
  # Enable verbose logging
  python main.py --verbose
  
  # Combine options
  python main.py --input-dir ./slides --processor advanced --output-dir ./extracted_advanced --verbose
        """
    )
    
    # Input/output options
    parser.add_argument(
        "--input-dir", "-i",
        type=str,
        default=None,
        help="Path to input directory containing documents (default: ./slides)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default=None,
        help="Path to output directory (default: ./extracted_text or ./extracted_advanced)"
    )
    
    # Processor options
    parser.add_argument(
        "--processor", "-p",
        type=str,
        choices=["simple", "advanced"],
        default=None,
        help="Processor type: simple or advanced (default: simple)"
    )
    
    # Configuration options
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="Path to YAML configuration file"
    )
    
    # Feature options
    parser.add_argument(
        "--questions", "-q",
        type=str,
        default=None,
        help="Path to JSON file with questions for Q&A (advanced only)"
    )
    
    parser.add_argument(
        "--enable-qna",
        action="store_true",
        help="Enable Q&A feature (advanced only)"
    )
    
    parser.add_argument(
        "--enable-annotations",
        action="store_true",
        help="Enable annotations feature (advanced only)"
    )
    
    # Logging options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce logging output"
    )
    
    return parser


def merge_configs(cli_args: argparse.Namespace, file_config: Dict[str, Any]) -> ProcessorConfig:
    """
    Merge CLI arguments with file configuration
    
    Args:
        cli_args: Command-line arguments
        file_config: Configuration from YAML file
        
    Returns:
        ProcessorConfig object
    """
    # Determine processor type
    processor_type = cli_args.processor or file_config["processor"]["type"]
    
    # Determine input directory
    input_dir = Path(cli_args.input_dir or file_config["processor"]["input_dir"])
    
    # Determine output directory
    if cli_args.output_dir:
        output_dir = Path(cli_args.output_dir)
    else:
        if processor_type == "advanced":
            output_dir = Path("./extracted_advanced")
        else:
            output_dir = Path("./extracted_text")
    
    # Update OCR config - convert string table_format to enum
    table_format_str = file_config["ocr"]["table_format"]
    try:
        from src.models.config import TableFormat
        table_format = TableFormat(table_format_str)
    except ValueError:
        # Default to markdown if invalid
        table_format = TableFormat.MARKDOWN
        print(f"Warning: Invalid table_format '{table_format_str}', using 'markdown'")
    
    ocr_config = OCRConfig(
        model=file_config["ocr"]["model"],
        table_format=table_format,
        extract_header=file_config["ocr"]["extract_header"],
        extract_footer=file_config["ocr"]["extract_footer"],
        include_image_base64=file_config["ocr"]["include_image_base64"],
        timeout=file_config["ocr"]["timeout"],
        max_retries=file_config["processor"]["max_retries"],
        retry_delay=file_config["processor"]["retry_delay"],
    )
    
    # Update QnA config
    qna_config = QnAConfig(
        enabled=cli_args.enable_qna or file_config["qna"]["enabled"],
        model=file_config["qna"]["model"],
        temperature=file_config["qna"]["temperature"],
        max_tokens=file_config["qna"]["max_tokens"],
        questions=file_config["qna"]["questions"],
    )
    
    # Update annotation config
    annotation_config = AnnotationConfig(
        enabled=cli_args.enable_annotations or file_config["annotations"]["enabled"],
        bbox_annotation_format=file_config["annotations"]["bbox_annotation_format"],
        document_annotation_format=file_config["annotations"]["document_annotation_format"],
        document_annotation_prompt=file_config["annotations"]["document_annotation_prompt"],
        include_image_base64=file_config["annotations"]["include_image_base64"],
    )
    
    # Load questions from file if provided
    if cli_args.questions:
        questions_path = Path(cli_args.questions)
        if questions_path.exists():
            import json
            with open(questions_path, 'r') as f:
                qna_config.questions = json.load(f)
    
    return ProcessorConfig(
        processor_type=processor_type,
        input_dir=input_dir,
        output_dir=output_dir,
        ocr_config=ocr_config,
        qna_config=qna_config,
        annotation_config=annotation_config,
        verbose=cli_args.verbose,
        quiet=cli_args.quiet,
    )


async def main_async(config: ProcessorConfig) -> bool:
    """
    Main async function
    
    Args:
        config: Processor configuration
        
    Returns:
        True if successful, False otherwise
    """
    print("=" * 60)
    print("Mistral OCR Pipeline")
    print("=" * 60)
    print(f"Processor: {config.processor_type}")
    print(f"Input directory: {config.input_dir}")
    print(f"Output directory: {config.output_dir}")
    print(f"OCR Model: {config.ocr_config.model}")
    
    if config.processor_type == "advanced":
        print(f"Q&A Enabled: {config.qna_config.enabled}")
        print(f"Annotations Enabled: {config.annotation_config.enabled}")
    
    print("=" * 60)
    
    # Check input directory
    if not config.input_dir.exists():
        print(f"Error: Input directory not found: {config.input_dir}")
        return False
    
    # Initialize processor
    try:
        if config.processor_type == "simple":
            processor = SimpleProcessor(config)
        else:
            processor = AdvancedProcessor(config)
        
        # Process documents
        print(f"\nProcessing documents in {config.input_dir}...")
        success = await processor.process_directory()
        
        if success:
            print("\n" + "=" * 60)
            print("Processing Complete!")
            print("=" * 60)
            print(f"Output saved to: {config.output_dir}")
            return True
        else:
            print("\n" + "=" * 60)
            print("Processing Completed with Errors")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    # Parse command-line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Load configuration
    config_path = Path(args.config) if args.config else None
    file_config = load_config(config_path)
    
    # Merge configurations
    config = merge_configs(args, file_config)
    
    # Setup logging
    setup_logging(verbose=config.verbose, quiet=config.quiet)
    
    # Run async main function
    try:
        success = asyncio.run(main_async(config))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()