---
name: pdf
description: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see REFERENCE.md. If you need to fill out a PDF form, read FORMS.md and follow its instructions.

## Quick Start

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Download PDF Files

### Using Web Scraper Tools

PDF download capabilities are available through various web scraping tools:

**Obscura (Recommended for Large Scale)**
```bash
# Download single PDF
obscura "https://example.com/document.pdf" --download-pdf

# Download PDF and extract text
obscura "https://example.com/document.pdf" --download-pdf --extract-text

# Batch download multiple PDFs
obscura "https://example.com/files/*.pdf" --batch --download-pdf --concurrency 10

# Download and process with PDF skill
obscura "https://example.com/document.pdf" \
  --download-pdf \
  --then "pdftotext output.pdf text.txt"
```

**WebScrape**
```bash
# Download PDF files
webscrape --selector "a[href$='.pdf']" --download

# Download multiple PDFs
webscrape "https://example.com/page1" --selector '.pdf-link' --download
webscrape "https://example.com/page2" --selector '.pdf-link' --download
```

### Using curl/wget (Basic)
```bash
# Direct download
curl -O "https://example.com/document.pdf"

# Download with headers
curl -H "Referer: https://example.com" -O "https://example.com/document.pdf"

# Resume interrupted download
curl -C - "https://example.com/document.pdf"
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

#### Subscripts and Superscripts

**IMPORTANT**: Never use Unicode subscript/superscript characters (₀₁₂₃₄₅₆₇₈₉, ⁰¹²³⁴⁵⁶⁷⁸⁹) in ReportLab PDFs. The built-in fonts do not include these glyphs, causing them to render as solid black boxes.

Instead, use ReportLab's XML markup tags in Paragraph objects:
```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# Subscripts: use <sub> tag
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# Superscripts: use <super> tag
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

For canvas-drawn text (not Paragraph objects), manually adjust font the size and position rather than using Unicode subscripts/superscripts.

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Complete PDF Workflow Example

### Full Automation Pipeline

This example demonstrates a complete PDF processing workflow from download to output:

```python
#!/usr/bin/env python3
"""
Complete PDF Processing Pipeline
Handles downloading, extracting, processing and converting PDFs
"""

import os
import subprocess
import pandas as pd
from pathlib import Path

def download_pdf(url, output_path):
    """Download PDF from URL"""
    print(f"Downloading: {url}")
    subprocess.run(["wget", "-O", output_path, url])
    print(f"Saved to: {output_path}")

def extract_text(pdf_path):
    """Extract text using pdfplumber"""
    print(f"Extracting text from: {pdf_path}")
    import pdfplumber
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for i, page in enumerate(pdf.pages):
            text += f"\n=== Page {i+1} ===\n"
            text += page.extract_text()
    
    return text

def extract_tables(pdf_path, output_excel):
    """Extract tables and save as Excel"""
    print(f"Extracting tables from: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append(df)
        
        if all_tables:
            combined_df = pd.concat(all_tables, ignore_index=True)
            combined_df.to_excel(output_excel, index=False)
            print(f"Tables saved to: {output_excel}")

def create_watermarked_pdf(input_pdf, watermark_text, output_pdf):
    """Create PDF with watermark"""
    print(f"Adding watermark to: {input_pdf}")
    from pypdf import PdfReader, PdfWriter
    
    # Simple watermark implementation
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    # Add watermark page
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    wm_c = canvas.Canvas("watermark.pdf", pagesize=letter)
    wm_c.drawString(200, 750, watermark_text)
    wm_c.rotate(45)
    wm_c.save()
    
    watermark = PdfReader("watermark.pdf").pages[0]
    
    for page in reader.pages:
        page.merge_page(watermark)
        writer.add_page(page)
    
    with open(output_pdf, "wb") as output:
        writer.write(output)

def ocr_scanned_pdf(pdf_path, output_text):
    """OCR scanned PDF"""
    print(f"Performing OCR on: {pdf_path}")
    import pytesseract
    from pdf2image import convert_from_path
    
    images = convert_from_path(pdf_path)
    text = ""
    for i, image in enumerate(images):
        text += f"\n=== Page {i+1} ===\n"
        text += pytesseract.image_to_string(image)
    
    with open(output_text, "w") as f:
        f.write(text)

def main():
    """Complete workflow"""
    url = "https://example.com/document.pdf"
    pdf_path = "document.pdf"
    
    # Step 1: Download
    download_pdf(url, pdf_path)
    
    # Step 2: Extract text
    text = extract_text(pdf_path)
    with open("extracted_text.txt", "w") as f:
        f.write(text)
    
    # Step 3: Extract tables
    extract_tables(pdf_path, "tables.xlsx")
    
    # Step 4: Add watermark
    create_watermarked_pdf(pdf_path, "CONFIDENTIAL", "watermarked.pdf")
    
    # Step 5: OCR if needed
    # ocr_scanned_pdf("scanned.pdf", "ocr_output.txt")

if __name__ == "__main__":
    main()
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Integration with Web Scraping Tools

### Obscura Integration Pattern

```bash
# Download + Process pipeline
obscura "https://example.com/document.pdf" \
  --download-pdf \
  --then "pdftotext output.pdf text.txt"

# Batch download with processing
obscura "https://example.com/*.pdf" \
  --batch --download-pdf \
  --concurrency 10 \
  --then "python3 process_all_pdfs.py"
```

### WebScrape Integration

```bash
# Download PDFs from specific selectors
webscrape "https://example.com" --selector "a[href$='.pdf']" --download

# Process downloaded files
webscrape --download --then "pdftotext *.pdf *.txt"
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Download PDF | Obscura | `obscura url --download-pdf` |
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see FORMS.md) | See FORMS.md |

## Next Steps

- For advanced pypdfium2 usage, see REFERENCE.md
- For JavaScript libraries (pdf-lib), see REFERENCE.md
- If you need to fill out a PDF form, follow the instructions in FORMS.md
- For troubleshooting guides, see REFERENCE.md
- For web-based PDF tools, use Obscura's download capabilities

(End of file - total 527 lines)
