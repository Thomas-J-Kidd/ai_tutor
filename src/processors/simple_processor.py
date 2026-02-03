"""
Simple processor for the Mistral OCR pipeline.
Based on the original mistral_ocr_extractor.py.
"""

import os
import time
import base64
import asyncio
import requests
import logging
from pathlib import Path
from typing import Dict, Any

from src.processors.base_processor import BaseProcessor
from src.models.config import ProcessorConfig, DocumentType
from src.models.results import ProcessingResult
from src.utils.file_utils import (
    detect_document_type,
    encode_file_to_base64_url,
)

logger = logging.getLogger(__name__)


class SimpleProcessor(BaseProcessor):
    """
    Simple OCR processor using direct HTTP API calls.
    Based on the original mistral_ocr_extractor.py.
    """
    
    def setup_api_client(self):
        """Setup API client for simple processor"""
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def process_file(self, file_path: Path) -> ProcessingResult:
        """
        Process a single file with OCR
        
        Args:
            file_path: Path to file to process
            
        Returns:
            ProcessingResult object
        """
        start_time = time.time()
        
        try:
            # Detect document type
            doc_type = detect_document_type(file_path)
            
            # Encode file to base64 URL
            data_url = encode_file_to_base64_url(file_path, doc_type)
            
            # Determine document type for API
            if doc_type == DocumentType.IMAGE:
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
                "model": self.config.ocr_config.model,
                "document": document_field,
                "table_format": self.config.ocr_config.table_format.value,
                "extract_header": self.config.ocr_config.extract_header,
                "extract_footer": self.config.ocr_config.extract_footer,
                "include_image_base64": self.config.ocr_config.include_image_base64,
            }
            
            # Make API request with retry logic
            response = None
            last_error = None
            
            for attempt in range(self.config.ocr_config.max_retries):
                try:
                    logger.debug(f"Processing {file_path.name} (attempt {attempt + 1}/{self.config.ocr_config.max_retries})")
                    
                    response = requests.post(
                        f"{self.base_url}/ocr",
                        headers=self.headers,
                        json=payload,
                        timeout=self.config.ocr_config.timeout
                    )
                    
                    if response.status_code == 200:
                        break
                    else:
                        last_error = f"API error {response.status_code}: {response.text}"
                        logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                        
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                
                if attempt < self.config.ocr_config.max_retries - 1:
                    await asyncio.sleep(self.config.ocr_config.retry_delay)
            
            # Check if all attempts failed
            if response is None or response.status_code != 200:
                processing_time = time.time() - start_time
                return ProcessingResult.from_api_response(
                    filename=file_path.name,
                    file_path=file_path,
                    document_type=doc_type.value,
                    api_response={},
                    processing_time=processing_time,
                    error=last_error or "Unknown error",
                )
            
            # Parse successful response
            response_dict = response.json()
            processing_time = time.time() - start_time
            
            # Create ProcessingResult
            result = ProcessingResult.from_api_response(
                filename=file_path.name,
                file_path=file_path,
                document_type=doc_type.value,
                api_response=response_dict,
                processing_time=processing_time,
            )
            
            # Update metadata with attempts
            result.metadata.attempts = self.config.ocr_config.max_retries
            
            logger.info(f"Successfully processed {file_path.name} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing {file_path.name}: {str(e)}")
            
            return ProcessingResult.from_api_response(
                filename=file_path.name,
                file_path=file_path,
                document_type=detect_document_type(file_path).value,
                api_response={},
                processing_time=processing_time,
                error=str(e),
            )