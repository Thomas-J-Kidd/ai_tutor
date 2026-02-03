# Mistral OCR Pipeline

A modular Python program that extracts text from documents (PDF, PPTX, DOCX, images) using Mistral OCR API and saves the output to markdown and JSON files for LLM RAG setup. Features a clean `src/` folder structure with configurable processors and CLI interface.

## Features

### Core Features
- ✅ **Multiple Document Types**: Support for PDF, PPTX, DOCX, and images (PNG, JPG, GIF, BMP, TIFF)
- ✅ **Two Processing Modes**: Simple processor (basic OCR) and Advanced processor (with Q&A and annotations)
- ✅ **RAG-Ready Output**: Creates JSONL files for vector database ingestion
- ✅ **Structured Output**: Markdown files with metadata, headers, footers, and tables
- ✅ **Error Handling**: Retry logic with configurable attempts and delays
- ✅ **Progress Tracking**: Real-time progress bars with tqdm

### Advanced Features
- ✅ **Document Q&A**: Ask questions about extracted content using Mistral chat models
- ✅ **Annotation Support**: Configurable annotation formats (bbox_annotation_format, document_annotation_format)
- ✅ **Image Extraction**: Support for image base64 encoding in responses
- ✅ **Cost Estimation**: Token usage tracking and cost calculation
- ✅ **YAML Configuration**: Flexible configuration via YAML files

## Project Structure

```
ai_tutor/
├── .env                          # API key configuration
├── requirements.txt              # Python dependencies
├── main.py                       # Main entry point with CLI arguments
├── config.yaml                   # YAML configuration file
├── README.md                     # This documentation
├── slides/                       # Input documents (user provides path)
│   └── ECEN5793/                 # Example structure
├── src/                          # Source code directory
│   ├── __init__.py
│   ├── processors/               # Processor implementations
│   │   ├── __init__.py
│   │   ├── base_processor.py     # Base processor class
│   │   ├── simple_processor.py   # Original simple processor
│   │   └── advanced_processor.py # New advanced processor
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration classes
│   │   └── results.py            # Result data classes
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── file_utils.py         # File operations
│       └── logging_utils.py      # Logging configuration
└── extracted_text/               # Output directory (created after run)
    ├── markdown/                 # Markdown files
    ├── json/                     # JSON files
    ├── rag_ready/                # RAG-ready JSONL output
    └── raw_responses/            # Raw API responses
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   - Ensure your `.env` file contains:
     ```
     MISTRAL_API_KEY=your_api_key_here
     ```
   - Get your API key from [Mistral AI](https://console.mistral.ai/)

3. **Prepare your slides:**
   - Place your documents in the `slides/` directory (or specify a custom directory)

## Usage

### Command-Line Interface

The `main.py` script provides a comprehensive CLI interface:

```bash
# Basic usage (defaults to simple processor, slides directory)
python main.py

# Specify input directory
python main.py --input-dir ./my_slides

# Use advanced processor
python main.py --processor advanced

# Specify output directory
python main.py --output-dir ./my_output

# Use configuration file
python main.py --config config.yaml

# Enable Q&A feature (advanced only)
python main.py --processor advanced --enable-qna

# Enable annotations feature (advanced only)
python main.py --processor advanced --enable-annotations

# Enable verbose logging
python main.py --verbose

# Combine options
python main.py --input-dir ./slides --processor advanced --output-dir ./extracted_advanced --verbose

# Show help
python main.py --help
```

### Configuration File

The `config.yaml` file provides detailed configuration options:

```yaml
processor:
  type: "advanced"                # "simple" or "advanced"
  input_dir: "./slides"
  output_dir: "./extracted_advanced"
  max_retries: 3
  retry_delay: 5

ocr:
  model: "mistral-ocr-latest"
  table_format: "markdown"        # "null", "markdown", or "html"
  extract_header: true
  extract_footer: true
  include_image_base64: false
  timeout: 120

qna:
  enabled: true
  model: "mistral-small-latest"
  temperature: 0.1
  max_tokens: 1000
  questions:
    - "What is the main topic of this document?"
    - "What are the key points or findings?"
    - "Who is the intended audience for this document?"

annotations:
  enabled: true
  include_image_base64: true
```

### Processor Comparison

| Feature | Simple Processor | Advanced Processor |
|---------|-----------------|-------------------|
| **OCR Processing** | ✅ | ✅ |
| **Multiple Document Types** | ✅ | ✅ |
| **Retry Logic** | ✅ | ✅ |
| **Markdown Output** | ✅ | ✅ |
| **JSON Output** | ✅ | ✅ |
| **RAG-Ready Output** | ✅ | ✅ |
| **Document Q&A** | ❌ | ✅ |
| **Annotations** | ❌ | ✅ |
| **Image Base64** | Optional | Configurable |
| **Custom Questions** | ❌ | ✅ |

## Output Files

### Directory Structure
```
extracted_text/  (or specified output directory)
├── markdown/
│   ├── document1.md
│   ├── document2.md
│   └── ...
├── json/
│   ├── document1_full.json
│   ├── document2_full.json
│   └── ...
├── rag_ready/
│   └── slides_chunked.jsonl     # For vector database ingestion
└── raw_responses/
    ├── document1_raw.json
    ├── document2_raw.json
    └── ...
```

### Markdown Files
Each document generates a `.md` file with:
- **Metadata**: Document type, processing time, status, pages, tokens used
- **Document Structure**: Page-by-page extraction with headers and footers
- **Content**: Cleaned markdown content (image placeholders removed)
- **Tables**: Extracted in markdown format
- **Hyperlinks**: Detected and listed
- **Annotations**: JSON annotations if enabled (advanced only)
- **Q&A Responses**: Questions and answers if enabled (advanced only)

### JSON Files
Each document generates a `_full.json` file with:
- Complete processing metadata
- Page-by-page results with dimensions, headers, footers, markdown
- Tables and hyperlinks
- Annotations and Q&A responses (if enabled)

### RAG-Ready Output
The `slides_chunked.jsonl` file contains:
- **Chunked content**: Paragraph-level chunks for vector embedding
- **Metadata**: Source file, page number, document type, processing details
- **JSONL format**: One JSON object per line for easy ingestion

## API Configuration

### OCR API Parameters
- **Model**: `mistral-ocr-latest`
- **Table format**: `null`, `markdown`, or `html`
- **Header extraction**: `True` or `False`
- **Footer extraction**: `True` or `False`
- **Image inclusion**: `True` or `False`

### Q&A API Parameters (Advanced Only)
- **Model**: `mistral-small-latest` (configurable)
- **Temperature**: 0.1 (configurable)
- **Max tokens**: 1000 (configurable)
- **Questions**: Customizable list of questions

### Annotation Parameters (Advanced Only)
- **Bounding box format**: Configurable JSON format
- **Document annotation format**: Configurable JSON format
- **Annotation prompt**: Custom prompt for annotation extraction
- **Image base64**: Include images in annotations

## Error Handling

- **API Errors**: Retry logic with configurable attempts and delays
- **File Errors**: Skip corrupted files and continue processing
- **Network Errors**: Timeout handling and connection retries
- **Validation**: Input validation and error messages
- **Progress Tracking**: Real-time progress with detailed logging

## Cost Estimation

The pipeline provides cost estimation based on:
- Mistral OCR pricing: ~$1 per 1M tokens
- Actual API usage statistics
- Page count and document size metrics
- Q&A token usage (if enabled)

## Customization

### Configuration Options
1. **YAML Config**: Modify `config.yaml` for default settings
2. **CLI Arguments**: Override config with command-line options
3. **Environment Variables**: API key via `.env` file

### Code Customization
1. **Processor Selection**: Choose between simple and advanced processors
2. **Output Structure**: Modify `file_utils.py` for custom output formats
3. **Chunking Strategy**: Adjust chunk size and method in `create_rag_output()`
4. **File Patterns**: Update `find_documents()` for different file extensions

## Requirements

- Python 3.8+
- Mistral API key with OCR access
- Internet connectivity for API calls
- Dependencies: `python-dotenv`, `mistralai`, `tqdm`, `PyYAML`

## Troubleshooting

1. **API Key Issues**: Verify `.env` file format and key validity
2. **Network Errors**: Check internet connectivity and firewall settings
3. **File Size Limits**: Large files may require compression or chunking
4. **Rate Limiting**: Implement delays if hitting API rate limits
5. **Configuration Errors**: Check YAML syntax and file paths

## Examples

### Process All Slides with Advanced Features
```bash
python main.py --processor advanced --enable-qna --enable-annotations --verbose
```

### Process Specific Directory
```bash
python main.py --input-dir ./lecture_slides --output-dir ./lecture_output --processor advanced
```

### Use Custom Configuration
```bash
python main.py --config custom_config.yaml --input-dir ./my_docs
```

### Quick Test with Simple Processor
```bash
python main.py --input-dir ./test_slides --processor simple --quiet
```

## License

This project is for educational and research purposes. Ensure you comply with Mistral AI's terms of service and API usage policies.
