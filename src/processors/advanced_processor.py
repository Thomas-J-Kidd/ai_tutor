"""
Advanced processor for the Mistral OCR pipeline.
Based on mistral_ocr_advanced_simple.py with all features enabled.
"""

import os
import time
import json
import asyncio
import requests
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.processors.base_processor import BaseProcessor
from src.models.config import ProcessorConfig, DocumentType
from src.models.results import ProcessingResult
from src.utils.file_utils import (
    detect_document_type,
    encode_file_to_base64_url,
)

logger = logging.getLogger(__name__)


class AdvancedProcessor(BaseProcessor):
    """
    Advanced OCR processor with all features enabled:
    - OCR processing with annotations
    - Document Q&A capabilities
    - Support for multiple document types
    - Enhanced error handling
    """
    
    def setup_api_client(self):
        """Setup API client for advanced processor"""
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def process_file(self, file_path: Path) -> ProcessingResult:
        """
        Process a single file with advanced OCR features
        
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
            
            # Prepare OCR request payload with all features
            payload = {
                "model": self.config.ocr_config.model,
                "document": document_field,
                "table_format": self.config.ocr_config.table_format.value,
                "extract_header": self.config.ocr_config.extract_header,
                "extract_footer": self.config.ocr_config.extract_footer,
                "include_image_base64": self.config.ocr_config.include_image_base64,
            }
            
            # Add annotation configuration if enabled and has actual annotation formats
            if self.config.annotation_config.enabled:
                annotation_config = {}
                has_annotation_config = False
                
                if self.config.annotation_config.bbox_annotation_format:
                    annotation_config["bbox_annotation_format"] = self.config.annotation_config.bbox_annotation_format
                    has_annotation_config = True
                
                if self.config.annotation_config.document_annotation_format:
                    annotation_config["document_annotation_format"] = self.config.annotation_config.document_annotation_format
                    has_annotation_config = True
                
                if self.config.annotation_config.document_annotation_prompt:
                    annotation_config["document_annotation_prompt"] = self.config.annotation_config.document_annotation_prompt
                    has_annotation_config = True
                
                # Note: include_image_base64 should not be in annotation_config
                # It should be at the root level of the payload if needed
                
                if has_annotation_config:
                    payload["annotation_config"] = annotation_config
                    logger.debug(f"Added annotation config: {list(annotation_config.keys())}")
                else:
                    logger.debug("Annotation enabled but no annotation formats specified, skipping annotation_config")
            
            # Make OCR API request with retry logic
            ocr_response = await self._make_api_request_with_retry(
                endpoint="/ocr",
                payload=payload,
                file_path=file_path,
                operation="OCR"
            )
            
            if ocr_response is None:
                processing_time = time.time() - start_time
                return ProcessingResult.from_api_response(
                    filename=file_path.name,
                    file_path=file_path,
                    document_type=doc_type.value,
                    api_response={},
                    processing_time=processing_time,
                    error="OCR processing failed after all retries",
                )
            
            # Parse OCR response
            ocr_response_dict = ocr_response.json()
            processing_time = time.time() - start_time
            
            # Create ProcessingResult from OCR response
            result = ProcessingResult.from_api_response(
                filename=file_path.name,
                file_path=file_path,
                document_type=doc_type.value,
                api_response=ocr_response_dict,
                processing_time=processing_time,
            )
            
            # Update metadata with attempts
            result.metadata.attempts = self.config.ocr_config.max_retries
            
            # Perform Q&A if enabled
            if self.config.qna_config.enabled and result.successful:
                qna_responses = await self._perform_document_qna(
                    file_path=file_path,
                    ocr_result=result,
                    questions=self.config.qna_config.questions
                )
                result.qna_responses = qna_responses
            
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
    
    async def _make_api_request_with_retry(self, endpoint: str, payload: Dict[str, Any], 
                                          file_path: Path, operation: str) -> Optional[requests.Response]:
        """
        Make API request with retry logic
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            file_path: File being processed
            operation: Operation name for logging
            
        Returns:
            Response object or None if all retries failed
        """
        last_error = None
        
        for attempt in range(self.config.ocr_config.max_retries):
            try:
                logger.debug(f"{operation} for {file_path.name} (attempt {attempt + 1}/{self.config.ocr_config.max_retries})")
                
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    json=payload,
                    timeout=self.config.ocr_config.timeout
                )
                
                if response.status_code == 200:
                    return response
                else:
                    last_error = f"API error {response.status_code}: {response.text}"
                    logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
            
            if attempt < self.config.ocr_config.max_retries - 1:
                await asyncio.sleep(self.config.ocr_config.retry_delay)
        
        logger.error(f"{operation} failed for {file_path.name} after {self.config.ocr_config.max_retries} attempts: {last_error}")
        return None
    
    async def _perform_document_qna(self, file_path: Path, ocr_result: ProcessingResult, 
                                   questions: List[str]) -> List[Dict[str, Any]]:
        """
        Perform Document Q&A on OCR result
        
        Args:
            file_path: Path to file
            ocr_result: OCR processing result
            questions: List of questions to ask
            
        Returns:
            List of Q&A responses
        """
        qna_responses = []
        
        # Extract document content for Q&A
        document_content = ""
        for page in ocr_result.pages:
            if page.markdown:
                # Clean image placeholders
                content = page.markdown
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    if not (line.strip().startswith('![') and 'img-' in line and '.jpeg' in line):
                        cleaned_lines.append(line)
                document_content += '\n'.join(cleaned_lines) + '\n\n'
        
        if not document_content.strip():
            logger.warning(f"No content extracted for Q&A from {file_path.name}")
            return qna_responses
        
        # Ask each question
        for question in questions:
            try:
                qna_response = await self._ask_question(
                    document_content=document_content,
                    question=question,
                    file_path=file_path
                )
                qna_responses.append(qna_response)
                
            except Exception as e:
                logger.error(f"Error asking question '{question}' for {file_path.name}: {str(e)}")
                qna_responses.append({
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "error": str(e)
                })
        
        return qna_responses
    
    async def _ask_question(self, document_content: str, question: str, 
                           file_path: Path) -> Dict[str, Any]:
        """
        Ask a single question about the document
        
        Args:
            document_content: Extracted document content
            question: Question to ask
            file_path: Path to file
            
        Returns:
            Q&A response dictionary
        """
        # Prepare Q&A payload
        payload = {
            "model": self.config.qna_config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions about documents based on the provided content."
                },
                {
                    "role": "user",
                    "content": f"Document content:\n\n{document_content}\n\nQuestion: {question}"
                }
            ],
            "temperature": self.config.qna_config.temperature,
            "max_tokens": self.config.qna_config.max_tokens,
        }
        
        # Make Q&A API request
        response = await self._make_api_request_with_retry(
            endpoint="/chat/completions",
            payload=payload,
            file_path=file_path,
            operation="Q&A"
        )
        
        if response is None:
            return {
                "question": question,
                "answer": "Failed to get answer after retries",
                "error": "Q&A API request failed"
            }
        
        response_dict = response.json()
        
        # Extract answer
        answer = ""
        if "choices" in response_dict and len(response_dict["choices"]) > 0:
            answer = response_dict["choices"][0].get("message", {}).get("content", "")
        
        # Extract usage info
        tokens_used = response_dict.get("usage", {}).get("total_tokens", 0)
        
        return {
            "question": question,
            "answer": answer.strip(),
            "model": self.config.qna_config.model,
            "tokens_used": tokens_used,
            "temperature": self.config.qna_config.temperature,
        }