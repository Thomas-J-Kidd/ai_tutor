# Mistral OCR PDF Text Extractor

A Python program that extracts text from PDF slides using Mistral OCR API and saves the output to markdown files for LLM RAG setup.

## Features

- ✅ Extracts text from PDF files using Mistral OCR API (`mistral-ocr-latest`)
- ✅ Saves output in markdown format with structured metadata
- ✅ Extracts headers and footers separately (as requested)
- ✅ Preserves document structure and formatting
- ✅ Creates RAG-ready JSONL output for vector databases
- ✅ Maintains original directory structure
- ✅ Includes progress tracking and error handling
- ✅ Provides cost estimation based on token usage

## Project Structure

```
.
├── .env                          # API key configuration
├── requirements.txt              # Python dependencies
├── mistral_ocr_extractor.py      # Main OCR extraction script
├── mistral_ocr_direct_api.py     # Direct API test script
├── test_mistral_ocr_simple.py    # Simple test script
├── slides/                       # Input PDF slides
│   └── ECEN5793/
│       ├── ECEN5793_1_1_intro.pdf
│       ├── ECEN5793_1_2_imagesPerception.pdf
│       ├── ECEN5793_2_1_Aquisition_Interpolation.pdf
│       └── ECEN5793_3_1_Registration.pdf
└── extracted_text/               # Output directory (created after run)
    ├── ECEN5793/                 # Organized by class
    │   ├── ECEN5793_1_1_intro.md
    │   ├── ECEN5793_1_2_imagesPerception.md
    │   ├── ECEN5793_2_1_Aquisition_Interpolation.md
    │   └── ECEN5793_3_1_Registration.md
    ├── raw_responses/            # Raw API responses for debugging
    │   └── ECEN5793/
    │       ├── ECEN5793_1_1_intro_raw.json
    │       ├── ECEN5793_1_2_imagesPerception_raw.json
    │       ├── ECEN5793_2_1_Aquisition_Interpolation_raw.json
    │       └── ECEN5793_3_1_Registration_raw.json
    ├── rag_ready/                # RAG-ready output
    │   └── slides_chunked.jsonl  # Chunked content for vector DB
    └── all_slides_consolidated.md # Consolidated summary
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   - Ensure your `.env` file contains:
     ```
     MISTAL_API_KEY=your_api_key_here
     ```
   - Get your API key from [Mistral AI](https://console.mistral.ai/)

## Usage

### Basic OCR Extraction
```bash
python mistral_ocr_extractor.py
```

This will:
1. Find all PDF files in the `slides/` directory
2. Process each PDF using Mistral OCR API
3. Save markdown files to `extracted_text/` with the same directory structure
4. Create raw JSON responses for debugging
5. Generate a consolidated summary file
6. Create RAG-ready JSONL output

### Test Scripts

- **Test API connectivity:**
  ```bash
  python test_mistral_ocr_simple.py
  ```

- **Direct API test (fallback):**
  ```bash
  python mistral_ocr_direct_api.py
  ```

## Output Files

### Markdown Files
Each PDF generates a corresponding `.md` file with:
- **Metadata**: Page count, processing time, OCR model
- **Document Structure**: Page-by-page extraction
- **Headers/Footers**: Separately extracted sections
- **Tables**: Extracted in markdown format
- **Hyperlinks**: Detected and listed

### RAG-Ready Output
The `slides_chunked.jsonl` file contains:
- **Chunked content**: Paragraph-level chunks for vector embedding
- **Metadata**: Source file, page number, processing details
- **JSONL format**: One JSON object per line for easy ingestion

### Consolidated Summary
`all_slides_consolidated.md` provides:
- Overview of all processed files
- Page counts and processing times
- First-page previews of each document
- Links to individual extraction files

## API Configuration

The script uses the following Mistral OCR API parameters:
- **Model**: `mistral-ocr-latest`
- **Table format**: `markdown`
- **Header extraction**: `True`
- **Footer extraction**: `True`
- **Image inclusion**: `False` (set to `True` if needed)

## Error Handling

- **API errors**: Retry logic and detailed error messages
- **File errors**: Skip corrupted files and continue processing
- **Network errors**: Timeout handling and connection retries
- **Progress tracking**: Real-time progress bars with tqdm

## Cost Estimation

The script provides cost estimation based on:
- Mistral OCR pricing: ~$1 per 1M tokens
- Page count and document size metrics
- Actual API usage statistics

## Customization

You can modify the following in `mistral_ocr_extractor.py`:

1. **Output directory**: Change `output_base_dir` in `main()`
2. **OCR parameters**: Modify payload in `extract_text_from_pdf()`
3. **Chunking strategy**: Adjust `create_rag_ready_output()` for different chunk sizes
4. **File patterns**: Update `find_pdf_files()` for different file extensions

## Requirements

- Python 3.8+
- Mistral API key with OCR access
- Internet connectivity for API calls

## Notes

- PDFs are encoded as base64 data URLs for API transmission
- The script preserves the original directory structure
- Raw API responses are saved for debugging and analysis
- Processing time varies based on PDF size and page count

## Troubleshooting

1. **API key issues**: Verify `.env` file format and key validity
2. **Network errors**: Check internet connectivity and firewall settings
3. **PDF size limits**: Large PDFs may require chunking or compression
4. **Rate limiting**: Implement delays if hitting API rate limits

## License

This project is for educational and research purposes. Ensure you comply with Mistral AI's terms of service and API usage policies.