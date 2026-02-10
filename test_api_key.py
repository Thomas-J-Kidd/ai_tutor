#!/usr/bin/env python3
"""
Test script to verify Mistral API key works with OCR API.
Tests both direct HTTP requests and official mistralai library.
"""

import os
import sys
import json
import base64
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
if not API_KEY:
    print("Error: MISTRAL_API_KEY not found in .env file")
    sys.exit(1)

print(f"Testing API key: {API_KEY[:8]}...")

# Test 1: Direct HTTP request (current code approach)
print("\n=== Test 1: Direct HTTP Request ===")
try:
    import requests
    
    # Create a simple test image (1x1 pixel black PNG) as base64
    # Base64 encoded 1x1 black PNG
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    data_url = f"data:image/png;base64,{test_image_base64}"
    
    payload = {
        "model": "mistral-ocr-latest",
        "document": {
            "type": "image_url",
            "image_url": data_url
        },
        "table_format": "markdown",
        "extract_header": False,
        "extract_footer": False,
        "include_image_base64": False,
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"Making request to https://api.mistral.ai/v1/ocr...")
    response = requests.post(
        "https://api.mistral.ai/v1/ocr",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text[:200]}...")
    
    if response.status_code == 200:
        print("✓ Direct HTTP request SUCCESS")
    elif response.status_code == 401:
        print("✗ Direct HTTP request FAILED: 401 Unauthorized")
        print("  - Check if API key is valid")
        print("  - Check if API key has OCR access enabled")
        print("  - Check billing/credits in Mistral console")
    else:
        print(f"✗ Direct HTTP request FAILED: {response.status_code}")
        
except Exception as e:
    print(f"✗ Direct HTTP request ERROR: {e}")

# Test 2: Official mistralai library
print("\n=== Test 2: Official mistralai Library ===")
try:
    from mistralai import Mistral
    
    client = Mistral(api_key=API_KEY)
    
    # Same test image
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    data_url = f"data:image/png;base64,{test_image_base64}"
    
    print("Making OCR request via mistralai client...")
    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "image_url",
            "image_url": data_url
        },
        table_format="markdown",
        extract_header=False,
        extract_footer=False,
        include_image_base64=False,
    )
    
    print(f"✓ Official library SUCCESS")
    print(f"  Model: {response.model}")
    print(f"  Pages processed: {len(response.pages)}")
    if response.pages:
        print(f"  First page markdown preview: {response.pages[0].markdown[:100]}...")
    
except Exception as e:
    print(f"✗ Official library ERROR: {e}")
    # Try to get more details
    import traceback
    traceback.print_exc()

print("\n=== Summary ===")
print("If both tests fail with 401, your API key is likely invalid or missing OCR access.")
print("Visit https://console.mistral.ai to:")
print("1. Verify API key is correct")
print("2. Ensure OCR feature is enabled for your account")
print("3. Check billing/credits balance")