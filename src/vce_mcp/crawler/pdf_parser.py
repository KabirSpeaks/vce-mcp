import io
import PyPDF2
import logging

logger = logging.getLogger(__name__)

def parse_pdf(content_bytes: bytes) -> tuple[str, list[dict]]:
    """
    Parses a PDF file from bytes.
    Returns the full text and a list of chunks (by page).
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(content_bytes))
        
        full_text = []
        chunks = []
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                full_text.append(page_text)
                chunks.append({
                    'content': page_text.strip(),
                    'page_number': i + 1,
                    'section': f"Page {i + 1}"
                })
                
        return "\n\n".join(full_text), chunks
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return "", []
