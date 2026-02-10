"""PDF extraction utilities."""

import io


def extract_pdf_text(pdf_content: bytes) -> str | None:
    """Extract text from PDF content.
    
    Args:
        pdf_content: Raw PDF file content
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        try:
            from pypdf import PdfReader
        except ImportError:
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                print("⚠️  PDF library not found. Install: pip install pypdf")
                return None
        
        pdf_file = io.BytesIO(pdf_content)
        reader = PdfReader(pdf_file)
        
        text_parts = []
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"[페이지 {page_num}]\n{page_text}\n")
        
        return '\n'.join(text_parts)
    
    except Exception as e:
        print(f"❌ PDF 추출 오류: {str(e)}")
        return None
