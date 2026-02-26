#!/usr/bin/env python3
"""
Enhanced Annotation Viewer for Mistral OCR Pipeline
Creates an HTML visualization of annotations with better image representation.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
import webbrowser
import base64


def load_annotation_data(json_path: Path) -> Dict[str, Any]:
    """Load annotation data from JSON file"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data


def parse_annotation(annotation_str: str) -> Dict[str, Any]:
    """Parse annotation string to dictionary"""
    if not annotation_str:
        return {}
    try:
        return json.loads(annotation_str)
    except json.JSONDecodeError:
        # Try to handle malformed JSON
        return {"raw": annotation_str}


def create_annotation_html(json_path: Path, output_path: Path) -> str:
    """Create HTML visualization of annotations"""
    data = load_annotation_data(json_path)
    
    # Parse document annotation
    document_annotation_str = data.get("annotations", "")
    document_annotation = parse_annotation(document_annotation_str) if document_annotation_str else {}
    
    pages = data.get("pages", [])
    
    # Build HTML step by step
    html_parts = []
    
    # HTML header
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Annotation Viewer - """ + json_path.name + """</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            display: flex;
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .sidebar {
            flex: 0 0 350px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow-y: auto;
            max-height: calc(100vh - 40px);
            position: sticky;
            top: 20px;
        }
        .main-content {
            flex: 1;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .document-info {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        .document-info h2 {
            color: #3498db;
        }
        .info-item {
            margin: 10px 0;
        }
        .info-label {
            font-weight: bold;
            color: #7f8c8d;
        }
        .info-value {
            margin-left: 10px;
        }
        .key-topics {
            margin-top: 15px;
        }
        .topic-list {
            list-style-type: none;
            padding-left: 0;
        }
        .topic-list li {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        .image-annotations {
            margin-top: 30px;
        }
        .annotation-card {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .annotation-card:hover {
            background: #e8f4fc;
            transform: translateX(5px);
        }
        .annotation-card.active {
            background: #d4edda;
            border-left-color: #28a745;
        }
        .annotation-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .annotation-type {
            background: #3498db;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .annotation-confidence {
            background: #2ecc71;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .annotation-description {
            margin: 10px 0;
            line-height: 1.5;
            font-size: 14px;
        }
        .annotation-coordinates {
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 5px;
        }
        .page-section {
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }
        .page-header {
            background: #2c3e50;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .page-number {
            font-weight: bold;
            font-size: 18px;
        }
        .page-dimensions {
            font-size: 12px;
            opacity: 0.8;
        }
        .page-visualization {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 20px;
            margin: 15px 0;
            position: relative;
            min-height: 400px;
        }
        .page-canvas {
            position: relative;
            width: 100%;
            height: 500px;
            background: linear-gradient(45deg, #e9ecef 25%, transparent 25%), 
                        linear-gradient(-45deg, #e9ecef 25%, transparent 25%), 
                        linear-gradient(45deg, transparent 75%, #e9ecef 75%), 
                        linear-gradient(-45deg, transparent 75%, #e9ecef 75%);
            background-size: 20px 20px;
            background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
            border: 2px solid #adb5bd;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .page-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: rgba(255, 255, 255, 0.9);
            z-index: 1;
        }
        .page-info {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .page-info h3 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .page-info p {
            margin: 5px 0;
            color: #6c757d;
        }
        .pdf-link {
            display: inline-block;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            transition: background 0.2s ease;
        }
        .pdf-link:hover {
            background: #2980b9;
        }
        .image-box {
            position: absolute;
            border: 2px solid #6c757d;
            background: rgba(108, 117, 125, 0.1);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .image-box:hover {
            background: rgba(108, 117, 125, 0.2);
            border-color: #495057;
        }
        .image-box.annotated {
            border-color: #e74c3c;
            background: rgba(231, 76, 60, 0.1);
        }
        .image-box.active {
            border-color: #28a745;
            background: rgba(40, 167, 69, 0.2);
            z-index: 10;
        }
        .image-label {
            position: absolute;
            background: #6c757d;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            transform: translateY(-100%);
            top: 0;
            left: 0;
            white-space: nowrap;
        }
        .image-box.annotated .image-label {
            background: #e74c3c;
        }
        .image-box.active .image-label {
            background: #28a745;
        }
        .image-details {
            margin-top: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 13px;
        }
        .image-details h4 {
            margin: 0 0 5px 0;
            color: #495057;
        }
        .image-details p {
            margin: 3px 0;
            color: #6c757d;
        }
        .annotation-popup {
            position: absolute;
            background: white;
            border: 2px solid #3498db;
            border-radius: 6px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            z-index: 100;
            max-width: 300px;
            display: none;
        }
        .annotation-popup h4 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .annotation-popup .type {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-bottom: 8px;
        }
        .annotation-popup .confidence {
            display: inline-block;
            background: #2ecc71;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 5px;
            margin-bottom: 8px;
        }
        .annotation-popup .description {
            font-size: 14px;
            line-height: 1.4;
            margin: 10px 0;
        }
        .annotation-popup .close {
            position: absolute;
            top: 5px;
            right: 10px;
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            color: #6c757d;
        }
        .stats {
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }
        .stat-box {
            flex: 1;
            background: #3498db;
            color: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            margin: 5px 0;
        }
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }
        .no-annotations {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-style: italic;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin: 15px 0;
        }
        .control-btn {
            padding: 8px 15px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .control-btn:hover {
            background: #5a6268;
        }
        .control-btn.active {
            background: #28a745;
        }
        @media (max-width: 1200px) {
            .container {
                flex-direction: column;
            }
            .sidebar {
                flex: none;
                max-height: none;
                position: static;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="document-info">
                <h2>Document Annotations</h2>""")
    
    # Document annotation info
    if isinstance(document_annotation, dict):
        if document_annotation.get("title"):
            html_parts.append(f'<div class="info-item"><span class="info-label">Title:</span><span class="info-value">{document_annotation.get("title", "N/A")}</span></div>')
        if document_annotation.get("author"):
            html_parts.append(f'<div class="info-item"><span class="info-label">Author:</span><span class="info-value">{document_annotation.get("author", "N/A")}</span></div>')
        if document_annotation.get("summary"):
            html_parts.append(f'<div class="info-item"><span class="info-label">Summary:</span><span class="info-value">{document_annotation.get("summary", "N/A")}</span></div>')
        
        # Key topics
        if document_annotation.get("key_topics"):
            html_parts.append('<div class="key-topics"><h3>Key Topics</h3><ul class="topic-list">')
            for topic in document_annotation.get("key_topics", []):
                html_parts.append(f'<li>{topic}</li>')
            html_parts.append('</ul></div>')
        
        # Stats
        html_parts.append('<div class="stats">')
        if "figures_count" in document_annotation:
            html_parts.append(f'<div class="stat-box"><div class="stat-number">{document_annotation.get("figures_count", 0)}</div><div class="stat-label">Figures</div></div>')
        if "tables_count" in document_annotation:
            html_parts.append(f'<div class="stat-box"><div class="stat-number">{document_annotation.get("tables_count", 0)}</div><div class="stat-label">Tables</div></div>')
        html_parts.append('</div>')
    else:
        html_parts.append('<div class="no-annotations">No document annotations found</div>')
    
    html_parts.append('</div>')
    
    # Collect image annotations
    image_annotations_list = []
    for page in pages:
        for image in page.get("images", []):
            annotation_str = image.get("image_annotation", "")
            if annotation_str:
                annotation = parse_annotation(annotation_str)
                if annotation:
                    image_annotations_list.append({
                        "page": page["page_number"],
                        "image_id": image.get("id", ""),
                        "coordinates": image,
                        "annotation": annotation
                    })
    
    # Image annotations sidebar
    html_parts.append(f'<div class="image-annotations"><h2>Image Annotations ({len(image_annotations_list)})</h2>')
    if image_annotations_list:
        for idx, ann in enumerate(image_annotations_list):
            annotation = ann["annotation"]
            if isinstance(annotation, dict):
                object_type = annotation.get("object_type", "Unknown")
                confidence = annotation.get("confidence", 0)
                description = annotation.get("description", "No description")
                
                html_parts.append(f'''
                <div class="annotation-card" data-annotation-id="{idx}" data-page="{ann["page"]}" data-image="{ann["image_id"]}">
                    <div class="annotation-header">
                        <span class="annotation-type">{object_type}</span>
                        <span class="annotation-confidence">{confidence:.2f}</span>
                    </div>
                    <div class="annotation-description">
                        {description}
                    </div>
                    <div class="annotation-coordinates">
                        Page {ann["page"]} • Image: {ann["image_id"]}
                    </div>
                </div>''')
            else:
                html_parts.append(f'''
                <div class="annotation-card" data-annotation-id="{idx}" data-page="{ann["page"]}" data-image="{ann["image_id"]}">
                    <div class="annotation-header">
                        <span class="annotation-type">Unknown</span>
                    </div>
                    <div class="annotation-description">
                        Raw annotation data
                    </div>
                    <div class="annotation-coordinates">
                        Page {ann["page"]} • Image: {ann["image_id"]}
                    </div>
                </div>''')
    else:
        html_parts.append('<div class="no-annotations">No image annotations found</div>')
    html_parts.append('</div></div>')
    
    # Main content
    html_parts.append(f'''<div class="main-content">
            <h1>Annotation Viewer: {json_path.name}</h1>
            <p>Showing annotations for document with {len(pages)} pages</p>
            <div class="controls">
                <button class="control-btn active" data-filter="all">Show All</button>
                <button class="control-btn" data-filter="annotated">Annotated Only</button>
                <button class="control-btn" data-filter="none">No Annotations</button>
            </div>''')
    
    # Pages
    for page_idx, page in enumerate(pages):
        page_num = page["page_number"]
        dimensions = page.get("dimensions", {})
        width = dimensions.get("width", 1000)
        height = dimensions.get("height", 1000)
        scale_factor = 0.8  # Scale down for display
        
        html_parts.append(f'''
            <div class="page-section" data-page="{page_num}">
                <div class="page-header">
                    <div class="page-number">Page {page_num}</div>
                    <div class="page-dimensions">{width} × {height} px • DPI: {dimensions.get("dpi", "N/A")} • {len(page.get("images", []))} images</div>
                </div>
                <div class="page-visualization">
                    <div class="page-canvas" data-page="{page_num}" data-width="{width}" data-height="{height}">
                        <div class="page-overlay">
                            <div class="page-info">
                                <h3>Page {page_num} Visualization</h3>
                                <p><strong>Dimensions:</strong> {width} × {height} pixels</p>
                                <p><strong>Images detected:</strong> {len(page.get("images", []))}</p>
                                <p><strong>Annotated images:</strong> {sum(1 for img in page.get("images", []) if img.get("image_annotation"))}</p>
                                <p><em>Note: Actual PDF page image is not available in the JSON data.</em></p>
                                <p><em>Colored boxes show detected image positions and annotations.</em></p>
                            </div>
                        </div>''')
        
        # Add image boxes to canvas
        for image_idx, image in enumerate(page.get("images", [])):
            image_id = image.get("id", f"img-{image_idx}")
            x1 = image.get("top_left_x", 0)
            y1 = image.get("top_left_y", 0)
            x2 = image.get("bottom_right_x", 0)
            y2 = image.get("bottom_right_y", 0)
            
            # Calculate relative positions (0-100%)
            rel_x1 = (x1 / width) * 100
            rel_y1 = (y1 / height) * 100
            rel_width = ((x2 - x1) / width) * 100
            rel_height = ((y2 - y1) / height) * 100
            
            has_annotation = bool(image.get("image_annotation"))
            annotation_class = "annotated" if has_annotation else ""
            
            html_parts.append(f'''
                        <div class="image-box {annotation_class}" 
                             data-image-id="{image_id}"
                             data-page="{page_num}"
                             style="left: {rel_x1}%; top: {rel_y1}%; width: {rel_width}%; height: {rel_height}%;">
                            <div class="image-label">{image_id}</div>
                        </div>''')
        
        html_parts.append('''                    </div>
                    
                    <div class="image-details" id="details-page-''' + str(page_num) + '''">
                        <h4>Image Details</h4>
                        <p>Click on an image box to see annotation details</p>
                        <p><strong>Legend:</strong> 
                            <span style="display: inline-block; width: 12px; height: 12px; background: rgba(108, 117, 125, 0.1); border: 2px solid #6c757d; margin: 0 5px;"></span> Detected image
                            <span style="display: inline-block; width: 12px; height: 12px; background: rgba(231, 76, 60, 0.1); border: 2px solid #e74c3c; margin: 0 5px 0 15px;"></span> Annotated image
                        </p>
                    </div>
                </div>''')
        
        # Add annotation popup
        html_parts.append(f'''
                <div class="annotation-popup" id="popup-page-{page_num}">
                    <button class="close">&times;</button>
                    <h4>Image Annotation</h4>
                    <div class="type">Type: <span id="popup-type">Unknown</span></div>
                    <div class="confidence">Confidence: <span id="popup-confidence">0.00</span></div>
                    <div class="description" id="popup-description">No description available</div>
                </div>
            </div>''')
    
    # Close main content and add JavaScript
    html_parts.append('''</div></div>
    
    <script>
        // Store annotation data
        const annotationData = ''' + json.dumps(image_annotations_list) + ''';
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Set up annotation card clicks
            document.querySelectorAll('.annotation-card').forEach(card => {
                card.addEventListener('click', function() {
                    const annotationId = this.getAttribute('data-annotation-id');
                    const pageNum = this.getAttribute('data-page');
                    const imageId = this.getAttribute('data-image');
                    
                    // Highlight card
                    document.querySelectorAll('.annotation-card').forEach(c => c.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Scroll to page
                    const pageSection = document.querySelector(`[data-page="${pageNum}"]`);
                    if (pageSection) {
                        pageSection.scrollIntoView({behavior: 'smooth'});
                        
                        // Highlight image box
                        document.querySelectorAll('.image-box').forEach(box => box.classList.remove('active'));
                        const imageBox = document.querySelector(`.image-box[data-image-id="${imageId}"][data-page="${pageNum}"]`);
                        if (imageBox) {
                            imageBox.classList.add('active');
                            imageBox.scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});
                        }
                    }
                });
            });
            
            // Set up image box clicks
            document.querySelectorAll('.image-box').forEach(box => {
                box.addEventListener('click', function() {
                    const imageId = this.getAttribute('data-image-id');
                    const pageNum = this.getAttribute('data-page');
                    
                    // Find annotation for this image
                    const annotation = annotationData.find(ann => 
                        ann.image_id === imageId && ann.page == pageNum
                    );
                    
                    if (annotation) {
                        // Show popup
                        const popup = document.getElementById(`popup-page-${pageNum}`);
                        const typeSpan = document.getElementById('popup-type');
                        const confidenceSpan = document.getElementById('popup-confidence');
                        const descriptionSpan = document.getElementById('popup-description');
                        
                        if (annotation.annotation && typeof annotation.annotation === 'object') {
                            typeSpan.textContent = annotation.annotation.object_type || 'Unknown';
                            confidenceSpan.textContent = (annotation.annotation.confidence || 0).toFixed(2);
                            descriptionSpan.textContent = annotation.annotation.description || 'No description';
                        }
                        
                        // Position popup near the image box
                        const rect = this.getBoundingClientRect();
                        popup.style.display = 'block';
                        popup.style.left = (rect.left + rect.width + 10) + 'px';
                        popup.style.top = (rect.top) + 'px';
                        
                        // Close button
                        popup.querySelector('.close').onclick = function() {
                            popup.style.display = 'none';
                        };
                        
                        // Update details panel
                        const detailsPanel = document.getElementById(`details-page-${pageNum}`);
                        detailsPanel.innerHTML = `
                            <h4>${imageId}</h4>
                            <p><strong>Type:</strong> ${annotation.annotation.object_type || 'Unknown'}</p>
                            <p><strong>Confidence:</strong> ${(annotation.annotation.confidence || 0).toFixed(2)}</p>
                            <p><strong>Description:</strong> ${annotation.annotation.description || 'No description'}</p>
                            <p><strong>Coordinates:</strong> x=${annotation.coordinates.top_left_x}, y=${annotation.coordinates.top_left_y}</p>
                        `;
                    }
                    
                    // Highlight this box
                    document.querySelectorAll('.image-box').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Highlight corresponding annotation card
                    document.querySelectorAll('.annotation-card').forEach(card => {
                        if (card.getAttribute('data-image') === imageId && card.getAttribute('data-page') == pageNum) {
                            document.querySelectorAll('.annotation-card').forEach(c => c.classList.remove('active'));
                            card.classList.add('active');
                        }
                    });
                });
            });
            
            // Set up filter buttons
            document.querySelectorAll('.control-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const filter = this.getAttribute('data-filter');
                    
                    // Update active button
                    document.querySelectorAll('.control-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Apply filter
                    document.querySelectorAll('.image-box').forEach(box => {
                        const hasAnnotation = box.classList.contains('annotated');
                        
                        if (filter === 'all') {
                            box.style.display = 'block';
                        } else if (filter === 'annotated') {
                            box.style.display = hasAnnotation ? 'block' : 'none';
                        } else if (filter === 'none') {
                            box.style.display = hasAnnotation ? 'none' : 'block';
                        }
                    });
                });
            });
            
            // Close popups when clicking outside
            document.addEventListener('click', function(event) {
                if (!event.target.closest('.annotation-popup') && !event.target.closest('.image-box')) {
                    document.querySelectorAll('.annotation-popup').forEach(popup => {
                        popup.style.display = 'none';
                    });
                }
            });
        });
    </script>
</body>
</html>''')
    
    html = ''.join(html_parts)
    
    # Write HTML to file
    with open(output_path, 'w') as f:
        f.write(html)
    
    return html


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Create HTML visualization of annotations")
    parser.add_argument("json_file", help="Path to JSON file with annotations")
    parser.add_argument("--output", "-o", help="Output HTML file path (default: annotations_viewer.html)")
    parser.add_argument("--open", action="store_true", help="Open the HTML file in browser after creation")
    
    args = parser.parse_args()
    
    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = json_path.parent / f"{json_path.stem}_annotations.html"
    
    print(f"Creating annotation visualization for {json_path.name}...")
    create_annotation_html(json_path, output_path)
    print(f"HTML visualization created: {output_path}")
    
    if args.open:
        print(f"Opening {output_path} in browser...")
        webbrowser.open(f"file://{output_path.absolute()}")


if __name__ == "__main__":
    main()
