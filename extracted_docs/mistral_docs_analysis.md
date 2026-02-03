# Mistral Documentation Analysis

*Generated from HTML files in: /home/zappiza/Documents/Projects/ai_tutor/mistral_docs*
*Total files processed: 4*

## OCR Capabilities

### OCR Processor | Mistral Docs

#### Content Preview

Capabilities
Document AI
OCR Processor
Copy markdown
Document AI - OCR Processor
Mistral Document AI API comes with a Document OCR (Optical Character Recognition) processor, powered by our latest OCR model
mistral-ocr-latest
, which enables you to extract text and structured content from PDF documents.
Before You Start
Copy section link
Before You Start
Key Features
Extracts text
in content while maintaining document structure and hierarchy.
Preserves formatting like headers, paragraphs, lists and tables.
Table formatting
can be toggled between
null
,
markdown
and
html
via the
table_format
parameter.
null
: Tables are returned inline as markdown within the extracted page.
markdown
: Tables are returned as markdown tables separately.
html
: Tables are returned as html tables separately.
Option to
extract headers and footers
via the
extract_header
and the
extract_footer
parameter, when used, the headers and footers content will be provided in the
header
and
footer
fields. By default, headers and footers are considered as part of the main content output.
Returns results in markdown format for easy parsing and rendering.
Handles complex layouts including multi-column text and mixed content and returns hyperlinks when available.
Processes documents at scale with high accuracy
Supports multiple document formats including:
image_url
: png, jpeg/jpg, avif and more...
document_url
: pdf, pptx, docx and more...
For a non-exaustive more comprehensive list, visit our
FAQ
.
Learn more about our API
here
.
i
Information
Table formatting as well as header and footer extraction is only available for OCR 2512 or newer.
The OCR processor returns the extracted
text content
,
images bboxes
and metadata about the document structure, making it easy to work with the recognized content programmatically.
OCR with Images and PDFs
Copy section link
OCR with Images and PDFs
OCR your Documents
We provide different methods to OCR your documents. You can either OCR a
PDF
or an
Image
.
PDFs
Copy s...

---

## Annotation Capabilities

### Annotations | Mistral Docs

#### Key Features
- bounding["\']?\s*box["\']?

#### Content Preview

Capabilities
Document AI
Annotations
Copy markdown
Annotations
In addition to the basic OCR functionality, Mistral Document AI API adds the
annotations
functionality, which allows you to extract information in a structured json-format that you provide.
Before You Start
Copy section link
Before You Start
What can you do with Annotations?
Specifically, it offers two types of annotations:
bbox_annotation
: gives you the annotation of the bboxes extracted by the OCR model (charts/ figures etc) based on user requirement and provided bbox/image annotation format. The user may ask to describe/caption the figure for instance.
document_annotation
: returns the annotation of the entire document based on the provided document annotation format.
Key Capabilities
Copy section link
Key Capabilities
Labeling and annotating data
Extraction and structuring of specific information from documents into a predefined JSON format
Automation of data extraction to reduce manual entry and errors
Efficient handling of large document volumes for enterprise-level applications
Common Use Cases
Copy section link
Common Use Cases
Parsing of forms, classification of documents, and processing of images, including text, charts, and signatures
Conversion of charts to tables, extraction of fine print from figures, or definition of custom image types
Capture of receipt data, including merchant names and transaction amounts, for expense management.
Extraction of key information like vendor details and amounts from invoices for automated accounting.
Extraction of key clauses and terms from contracts for easier review and management
How it Works
Copy section link
How it Works
BBOX Annotations
Copy section link
BBOX Annotations
All document types:
After regular OCR is finished; we call a Vision capable LLM for all bboxes individually with the provided annotation format.
Document Annotation
Copy section link
Document Annotation
All document types:
We run OCR and send the output text in Markdown, along with t...

---

## Document Q&A Capabilities

### Document QnA | Mistral Docs

#### Key Features
- q&a["\']?
- question["\']?\s*answering

#### Content Preview

Capabilities
Document AI
Document QnA
Copy markdown
Document AI QnA
The Document QnA capability combines OCR with large language model capabilities to enable natural language interaction with document content. This allows you to extract information and insights from documents by asking questions in natural language.
tip
Before continuing, we recommend reading the
Chat Completions
documentation to learn more about the chat completions API and how to use it before proceeding.
Before You Start
Copy section link
Before You Start
Workflow and Capabilities
The workflow consists of two main steps:
Document Processing: OCR extracts text, structure, and formatting, creating a machine-readable version of the document.
Language Model Understanding: The extracted document content is analyzed by a large language model. You can ask questions or request information in natural language. The model understands context and relationships within the document and can provide relevant answers based on the document content.
Key Capabilities
Copy section link
Key Capabilities
Question answering about specific document content
Information extraction and summarization
Document analysis and insights
Multi-document queries and comparisons
Context-aware responses that consider the full document
Common Use Cases
Copy section link
Common Use Cases
Analyzing research papers and technical documents
Extracting information from business documents
Processing legal documents and contracts
Building document Q&A applications
Automating document-based workflows
Usage
Copy section link
Usage
Leverage Document QnA
The examples below show how to interact with a PDF document using natural language.
QnA with a PDF Url
QnA with a Base64 Encoded PDF
QnA with an Uploaded PDF
Close
Be sure the URL is
public
and accessible by our API.
python
typescript
curl
Output
import
os
from
mistralai
import
Mistral
api_key
=
os
.
environ
[
"MISTRAL_API_KEY"
]
model
=
"mistral-small-latest"
client
=
Mistral
(
api_key
=
api_key
)...

---

## Other Documentation

### Mistral Docs

#### Content Preview

Capabilities
Document AI
Copy markdown
Document AI
Mistral Document AI offers enterprise-level document processing, combining cutting-edge OCR technology with advanced structured data extraction. Experience faster processing speeds, unparalleled accuracy, and cost-effective solutions, all scalable to meet your needs.
Unlock the full potential of your documents with our multilingual support, annotations and adaptable workflows for all document types, enabling you to extract, comprehend, and analyze information with ease.
Document AI Services
Copy section link
Document AI Services
Using
client.ocr.process
in our SDK Clients as the entry point and/or the
https://api.mistral.ai/v1/ocr
endpoint, you can access the following services from our Document AI stack:
OCR Processor
: Discover our OCR model and its extensive capabilities.
Annotations
: Annotate and extract data from your documents using our built-in Structured Outputs.
Document QnA
: Harness the power of our vast models in conjunction with our OCR technology.

Document AI
Mistral Document AI offers enterprise-level document processing, combining cutting-edge OCR technology with advanced structured data extraction. Experience faster processing speeds, unparalleled accuracy, and cost-effective solutions, all scalable to meet your needs.
Unlock the full potential of your documents with our multilingual support, annotations and adaptable workflows for all document types, enabling you to extract, comprehend, and analyze information with ease.
Document AI Services
Copy section link
Document AI Services
Using
client.ocr.process
in our SDK Clients as the entry point and/or the
https://api.mistral.ai/v1/ocr
endpoint, you can access the following services from our Document AI stack:
OCR Processor
: Discover our OCR model and its extensive capabilities.
Annotations
: Annotate and extract data from your documents using our built-in Structured Outputs.
Document QnA
: Harness the power of our vast models in conjunction with ou...

---

## Summary

- **Total sections extracted**: 4
- **OCR sections**: 1
- **Annotation sections**: 1
- **Q&A sections**: 1

### Key Features Identified
- bounding["\']?\s*box["\']?
- q&a["\']?
- question["\']?\s*answering
