#!/usr/bin/env python3
"""
Extract text from Mistral documentation HTML files.
This script processes HTML files in the mistral_docs directory and extracts
structured information about Mistral's OCR capabilities.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class DocumentationSection:
    """Represents a section of Mistral documentation"""
    title: str
    content: str
    url: Optional[str] = None
    features: List[str] = None
    api_endpoints: List[str] = None
    parameters: Dict[str, str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.api_endpoints is None:
            self.api_endpoints = []
        if self.parameters is None:
            self.parameters = {}


class MistralDocsExtractor:
    """Extracts and processes Mistral documentation from HTML files"""
    
    def __init__(self, docs_dir: Path):
        """
        Initialize extractor with documentation directory
        
        Args:
            docs_dir: Path to mistral_docs directory
        """
        self.docs_dir = docs_dir
        self.sections: List[DocumentationSection] = []
        
    def extract_from_html(self, html_path: Path) -> List[DocumentationSection]:
        """
        Extract text and structure from HTML file
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            List of DocumentationSection objects
        """
        print(f"Processing: {html_path.name}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get page title
        title = soup.title.string if soup.title else html_path.stem
        
        # Extract main content - look for common content containers
        content_areas = []
        
        # Try to find main content areas
        for selector in ['main', 'article', '.content', '#content', 'body']:
            elements = soup.select(selector)
            if elements:
                content_areas.extend(elements)
        
        # If no specific content areas found, use body
        if not content_areas:
            content_areas = [soup.body] if soup.body else []
        
        # Extract text from content areas
        full_text = ""
        for area in content_areas:
            if area:
                # Get text with reasonable spacing
                text = area.get_text(separator='\n', strip=True)
                # Clean up excessive whitespace
                text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
                full_text += text + "\n\n"
        
        # Try to extract specific information based on file name
        sections = []
        filename = html_path.stem.lower()
        
        if 'ocr' in filename:
            section = self._extract_ocr_info(title, full_text, html_path)
            sections.append(section)
        elif 'annotation' in filename:
            section = self._extract_annotation_info(title, full_text, html_path)
            sections.append(section)
        elif 'qna' in filename or 'q&a' in filename:
            section = self._extract_qna_info(title, full_text, html_path)
            sections.append(section)
        else:
            # General documentation
            section = DocumentationSection(
                title=title,
                content=full_text[:5000] + "..." if len(full_text) > 5000 else full_text,
                url=self._extract_url_from_filename(html_path)
            )
            sections.append(section)
        
        return sections
    
    def _extract_ocr_info(self, title: str, content: str, html_path: Path) -> DocumentationSection:
        """Extract OCR-specific information"""
        section = DocumentationSection(
            title=title,
            content=content[:10000] + "..." if len(content) > 10000 else content,
            url=self._extract_url_from_filename(html_path)
        )
        
        # Look for OCR features
        ocr_patterns = [
            r'model["\']?\s*:\s*["\']([^"\']+)["\']',
            r'ocr["\']?\s*:\s*["\']([^"\']+)["\']',
            r'extract["\']?\s*:\s*["\']([^"\']+)["\']',
            r'table["\']?\s*:\s*["\']([^"\']+)["\']',
            r'header["\']?\s*:\s*["\']([^"\']+)["\']',
            r'footer["\']?\s*:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in ocr_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                section.features.extend(matches)
        
        # Look for API endpoints
        api_patterns = [
            r'POST\s+([/\w-]+ocr[/\w-]*)',
            r'endpoint["\']?\s*:\s*["\']([^"\']+)["\']',
            r'https?://api\.mistral\.ai[^\s]+',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                section.api_endpoints.extend(matches)
        
        # Look for parameters
        param_pattern = r'["\']?(\w+)["\']?\s*:\s*{[^}]+}'
        matches = re.findall(param_pattern, content)
        if matches:
            for match in matches:
                section.parameters[match] = "Found in documentation"
        
        return section
    
    def _extract_annotation_info(self, title: str, content: str, html_path: Path) -> DocumentationSection:
        """Extract annotation-specific information"""
        section = DocumentationSection(
            title=title,
            content=content[:10000] + "..." if len(content) > 10000 else content,
            url=self._extract_url_from_filename(html_path)
        )
        
        # Look for annotation features
        annotation_patterns = [
            r'annotation["\']?\s*:\s*["\']([^"\']+)["\']',
            r'bounding["\']?\s*box["\']?',
            r'entity["\']?\s*recognition',
            r'text["\']?\s*detection',
        ]
        
        for pattern in annotation_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                section.features.append(pattern.replace('["\']?', '').replace('["\']', ''))
        
        return section
    
    def _extract_qna_info(self, title: str, content: str, html_path: Path) -> DocumentationSection:
        """Extract Q&A-specific information"""
        section = DocumentationSection(
            title=title,
            content=content[:10000] + "..." if len(content) > 10000 else content,
            url=self._extract_url_from_filename(html_path)
        )
        
        # Look for Q&A features
        qna_patterns = [
            r'q&a["\']?',
            r'question["\']?\s*answering',
            r'context["\']?\s*extraction',
            r'answer["\']?\s*generation',
        ]
        
        for pattern in qna_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                section.features.append(pattern.replace('["\']?', '').replace('["\']', ''))
        
        return section
    
    def _extract_url_from_filename(self, html_path: Path) -> Optional[str]:
        """Try to extract URL from filename or content"""
        # Check if we have a urls.md file
        urls_file = self.docs_dir / "urls.md"
        if urls_file.exists():
            try:
                with open(urls_file, 'r') as f:
                    urls_content = f.read()
                    # Look for URL that might match this file
                    filename_stem = html_path.stem
                    for line in urls_content.split('\n'):
                        if line.strip() and filename_stem.lower() in line.lower():
                            return line.strip()
            except:
                pass
        
        return None
    
    def process_all_files(self):
        """Process all HTML files in the documentation directory"""
        html_files = list(self.docs_dir.glob("*.html"))
        
        if not html_files:
            print(f"No HTML files found in {self.docs_dir}")
            return
        
        print(f"Found {len(html_files)} HTML files to process")
        
        for html_file in html_files:
            try:
                sections = self.extract_from_html(html_file)
                self.sections.extend(sections)
                print(f"  ✓ Extracted {len(sections)} section(s) from {html_file.name}")
            except Exception as e:
                print(f"  ✗ Error processing {html_file.name}: {e}")
    
    def save_to_markdown(self, output_path: Path):
        """Save extracted documentation to markdown file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = "# Mistral Documentation Analysis\n\n"
        md_content += f"*Generated from HTML files in: {self.docs_dir}*\n"
        md_content += f"*Total files processed: {len(set(s.title for s in self.sections))}*\n\n"
        
        # Group by type
        ocr_sections = [s for s in self.sections if 'ocr' in s.title.lower()]
        annotation_sections = [s for s in self.sections if 'annotation' in s.title.lower()]
        qna_sections = [s for s in self.sections if 'qna' in s.title.lower() or 'q&a' in s.title.lower()]
        other_sections = [s for s in self.sections if s not in ocr_sections + annotation_sections + qna_sections]
        
        if ocr_sections:
            md_content += "## OCR Capabilities\n\n"
            for section in ocr_sections:
                md_content += f"### {section.title}\n\n"
                if section.url:
                    md_content += f"**Source**: {section.url}\n\n"
                
                if section.features:
                    md_content += "#### Key Features\n"
                    for feature in section.features:
                        md_content += f"- {feature}\n"
                    md_content += "\n"
                
                if section.api_endpoints:
                    md_content += "#### API Endpoints\n"
                    for endpoint in section.api_endpoints:
                        md_content += f"- `{endpoint}`\n"
                    md_content += "\n"
                
                if section.parameters:
                    md_content += "#### Parameters\n"
                    for param, desc in section.parameters.items():
                        md_content += f"- `{param}`: {desc}\n"
                    md_content += "\n"
                
                # Add content preview
                preview = section.content[:2000]
                if len(section.content) > 2000:
                    preview += "..."
                md_content += f"#### Content Preview\n\n{preview}\n\n"
                md_content += "---\n\n"
        
        if annotation_sections:
            md_content += "## Annotation Capabilities\n\n"
            for section in annotation_sections:
                md_content += f"### {section.title}\n\n"
                if section.url:
                    md_content += f"**Source**: {section.url}\n\n"
                
                if section.features:
                    md_content += "#### Key Features\n"
                    for feature in section.features:
                        md_content += f"- {feature}\n"
                    md_content += "\n"
                
                preview = section.content[:2000]
                if len(section.content) > 2000:
                    preview += "..."
                md_content += f"#### Content Preview\n\n{preview}\n\n"
                md_content += "---\n\n"
        
        if qna_sections:
            md_content += "## Document Q&A Capabilities\n\n"
            for section in qna_sections:
                md_content += f"### {section.title}\n\n"
                if section.url:
                    md_content += f"**Source**: {section.url}\n\n"
                
                if section.features:
                    md_content += "#### Key Features\n"
                    for feature in section.features:
                        md_content += f"- {feature}\n"
                    md_content += "\n"
                
                preview = section.content[:2000]
                if len(section.content) > 2000:
                    preview += "..."
                md_content += f"#### Content Preview\n\n{preview}\n\n"
                md_content += "---\n\n"
        
        if other_sections:
            md_content += "## Other Documentation\n\n"
            for section in other_sections:
                md_content += f"### {section.title}\n\n"
                if section.url:
                    md_content += f"**Source**: {section.url}\n\n"
                
                preview = section.content[:2000]
                if len(section.content) > 2000:
                    preview += "..."
                md_content += f"#### Content Preview\n\n{preview}\n\n"
                md_content += "---\n\n"
        
        # Add summary
        md_content += "## Summary\n\n"
        md_content += f"- **Total sections extracted**: {len(self.sections)}\n"
        md_content += f"- **OCR sections**: {len(ocr_sections)}\n"
        md_content += f"- **Annotation sections**: {len(annotation_sections)}\n"
        md_content += f"- **Q&A sections**: {len(qna_sections)}\n"
        
        # Extract key insights
        all_features = []
        for section in self.sections:
            all_features.extend(section.features)
        
        if all_features:
            unique_features = list(set(all_features))
            md_content += f"\n### Key Features Identified\n"
            for feature in sorted(unique_features):
                md_content += f"- {feature}\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\nSaved documentation analysis to: {output_path}")
        return output_path
    
    def save_to_json(self, output_path: Path):
        """Save extracted documentation to JSON file for programmatic use"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "sections": [asdict(section) for section in self.sections],
            "summary": {
                "total_sections": len(self.sections),
                "ocr_sections": len([s for s in self.sections if 'ocr' in s.title.lower()]),
                "annotation_sections": len([s for s in self.sections if 'annotation' in s.title.lower()]),
                "qna_sections": len([s for s in self.sections if 'qna' in s.title.lower() or 'q&a' in s.title.lower()]),
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved structured data to: {output_path}")
        return output_path


def main():
    """Main execution function"""
    import sys
    
    # Define directories
    project_root = Path(__file__).parent
    docs_dir = project_root / "mistral_docs"
    output_dir = project_root / "extracted_docs"
    
    print("=" * 60)
    print("Mistral Documentation Extractor")
    print("=" * 60)
    print(f"Documentation directory: {docs_dir}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    # Create extractor and process files
    extractor = MistralDocsExtractor(docs_dir)
    extractor.process_all_files()
    
    if not extractor.sections:
        print("\nNo documentation extracted. Exiting.")
        return
    
    # Save outputs
    output_dir.mkdir(exist_ok=True)
    
    md_path = output_dir / "mistral_docs_analysis.md"
    extractor.save_to_markdown(md_path)
    
    json_path = output_dir / "mistral_docs_structured.json"
    extractor.save_to_json(json_path)
    
    print("\n" + "=" * 60)
    print("Extraction Complete!")
    print("=" * 60)
    print(f"✓ Markdown analysis: {md_path}")
    print(f"✓ Structured JSON: {json_path}")
    print(f"✓ Total sections extracted: {len(extractor.sections)}")
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