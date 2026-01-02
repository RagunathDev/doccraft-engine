from PyPDF2 import PdfReader, PdfWriter
import os

def merge_pdfs(pdf_paths, output_path):
    """
    Merges multiple PDF files into one.
    """
    try:
        writer = PdfWriter()
        for path in pdf_paths:
            if os.path.exists(path):
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        return True, output_path
    except Exception as e:
        return False, str(e)

def split_pdf(pdf_path, output_dir, page_ranges):
    """
    Splits a PDF by page ranges (e.g., '1-2, 3, 5-10').
    """
    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        # Simple implementation for page ranges
        # Expects list of single pages or ranges: [0, 1, 2-4]
        results = []
        for i, range_str in enumerate(page_ranges):
            writer = PdfWriter()
            if '-' in str(range_str):
                start, end = map(int, range_str.split('-'))
                for p in range(max(0, start-1), min(total_pages, end)):
                    writer.add_page(reader.pages[p])
            else:
                p = int(range_str) - 1
                if 0 <= p < total_pages:
                    writer.add_page(reader.pages[p])
            
            out_file = os.path.join(output_dir, f"split_part_{i+1}.pdf")
            with open(out_file, "wb") as f:
                writer.write(f)
            results.append(out_file)
            
        return True, results
    except Exception as e:
        return False, str(e)

def rotate_pages(pdf_path, output_path, rotation_map):
    """
    Rotates specific pages in a PDF.
    rotation_map: {page_index: angle} (angle: 90, 180, 270)
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        for i, page in enumerate(reader.pages):
            if str(i) in rotation_map:
                page.rotate(rotation_map[str(i)])
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
        return True, output_path
    except Exception as e:
        return False, str(e)

def delete_pages(pdf_path, output_path, pages_to_delete):
    """
    Deletes specific pages from a PDF.
    pages_to_delete: list of 1-indexed page numbers
    """
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        delete_set = set(map(int, pages_to_delete))
        for i, page in enumerate(reader.pages):
            if (i + 1) not in delete_set:
                writer.add_page(page)
                
        with open(output_path, "wb") as f:
            writer.write(f)
        return True, output_path
    except Exception as e:
        return False, str(e)
