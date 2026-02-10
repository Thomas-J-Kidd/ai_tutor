"""
Base processor class for the Mistral OCR pipeline.
"""

import os
import json
import time
import asyncio
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from mistralai import Mistral

from src.models.config import ProcessorConfig
from src.models.results import ProcessingResult
from src.utils.file_utils import (
    find_documents,
    create_output_directories,
    save_markdown,
    save_json,
    create_rag_output,
)

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """
    Base class for all OCR processors.
    """
    
    def __init__(self, config: ProcessorConfig):
        """
        Initialize the processor
        
        Args:
            config: Processor configuration
        """
        self.config = config
        self.results: List[ProcessingResult] = []
        
        # Load API key from environment
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY not found in .env file\n"
                "Please add your API key to the .env file:\n"
                "1. Get an API key from https://console.mistral.ai/api-keys/\n"
                "2. Add 'MISTRAL_API_KEY=your_key_here' to .env file"
            )
        
        # Validate API key format (basic check)
        if len(self.api_key) != 32:
            logger.warning(
                f"API key length is {len(self.api_key)} characters (expected 32). "
                "This may not be a valid Mistral API key."
            )
        
        # Setup API client
        self.setup_api_client()
    
    def setup_api_client(self):
        """Setup API client for the processor"""
        # Get optional server configuration from environment
        # Valid server values: 'eu' (default) or '' (global)
        # server_url: custom URL override
        server = os.getenv("MISTRAL_SERVER")
        server_url = os.getenv("MISTRAL_SERVER_URL")
        
        # Build kwargs with explicit typing to avoid type errors
        kwargs: Dict[str, Any] = {"api_key": self.api_key}
        
        # Add server if provided (can be empty string for global)
        if server is not None:
            kwargs["server"] = server
            
        # Add server_url if provided
        if server_url is not None:
            kwargs["server_url"] = server_url
            
        self.client = Mistral(**kwargs)
        
        # Log configuration
        config_info = []
        if server is not None:
            config_info.append(f"server={server}")
        if server_url is not None:
            config_info.append(f"server_url={server_url}")
        if not config_info:
            config_info.append("server=eu (default)")
            
        logger.debug(f"Mistral client configured with: {', '.join(config_info)}")
        logger.info(
            "If authentication fails (401), please check:\n"
            "1. Your API key is valid and active at https://console.mistral.ai/api-keys/\n"
            "2. You have sufficient credits/billing setup\n"
            "3. The API key has proper permissions for OCR endpoints"
        )
    
    @abstractmethod
    async def process_file(self, file_path: Path) -> ProcessingResult:
        """
        Process a single file
        
        Args:
            file_path: Path to file to process
            
        Returns:
            ProcessingResult object
        """
        pass
    
    async def process_directory(self) -> bool:
        """
        Process all documents in the input directory
        
        Returns:
            True if successful, False otherwise
        """
        # Find documents
        documents = find_documents(self.config.input_dir)
        
        if not documents:
            logger.error(f"No documents found in {self.config.input_dir}")
            return False
        
        logger.info(f"Found {len(documents)} documents to process")
        
        # Create output directories
        output_dirs = create_output_directories(self.config.output_dir)
        
        # Process each document
        successful = 0
        failed = 0
        
        for doc_path in tqdm(documents, desc="Processing documents"):
            try:
                result = await self.process_file(doc_path)
                self.results.append(result)
                
                if result.successful:
                    successful += 1
                    
                    # Save results
                    save_markdown(result, output_dirs["markdown"])
                    save_json(result, output_dirs["json"])
                    
                    logger.info(f"✓ Processed {doc_path.name}: {result.page_count} pages, "
                              f"{result.tokens_used} tokens")
                else:
                    failed += 1
                    logger.error(f"✗ Failed to process {doc_path.name}: {result.metadata.error}")
                    
            except Exception as e:
                failed += 1
                logger.error(f"✗ Error processing {doc_path.name}: {str(e)}")
        
        # Create RAG output if we have successful results
        if successful > 0:
            rag_path = create_rag_output(self.results, output_dirs["rag"])
            if rag_path:
                logger.info(f"Created RAG output: {rag_path}")
        
        # Print summary
        self.print_summary(successful, failed)
        
        return successful > 0
    
    def print_summary(self, successful: int, failed: int) -> None:
        """
        Print processing summary
        
        Args:
            successful: Number of successful documents
            failed: Number of failed documents
        """
        total = successful + failed
        
        print("\n" + "=" * 60)
        print("Processing Summary")
        print("=" * 60)
        print(f"Total documents: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        if successful > 0:
            total_pages = sum(r.page_count for r in self.results if r.successful)
            total_tokens = sum(r.tokens_used for r in self.results if r.successful)
            total_time = sum(r.processing_time for r in self.results if r.successful)
            
            print(f"Total pages: {total_pages}")
            print(f"Total tokens used: {total_tokens}")
            print(f"Total processing time: {total_time:.2f}s")
            print(f"Average processing time: {total_time/successful:.2f}s per document")
            print(f"Estimated cost: ${total_tokens / 1_000_000:.4f}")
            print(f"Output directory: {self.config.output_dir}")
        
        print("=" * 60)
    
    def save_raw_response(self, response: Dict[str, Any], file_path: Path, 
                         output_dir: Path) -> Path:
        """
        Save raw API response
        
        Args:
            response: Raw API response
            file_path: Original file path
            output_dir: Directory to save raw response
            
        Returns:
            Path to saved raw response file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        json_filename = file_path.name.rsplit('.', 1)[0] + '_raw.json'
        output_path = output_dir / json_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, default=str)
        
        return output_path