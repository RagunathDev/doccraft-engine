import img2pdf
from PIL import Image
import io
import os

def convert_images_to_pdf(image_paths, output_path):
    """
    Converts a list of image paths to a single PDF file.
    Supports JPG, PNG, GIF, BMP, TIFF, WebP.
    """
    try:
        # Filter supported formats and ensure they exist
        valid_images = []
        for path in image_paths:
            if os.path.exists(path):
                # Process image to ensure it's compatible (especially for non-JPG/PNG)
                try:
                    with Image.open(path) as img:
                        # Convert to RGB if necessary (Alpha channel can cause issues in img2pdf)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # Save to a temporary buffer as JPEG for maximum compatibility
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=95)
                        valid_images.append(buf.getvalue())
                except Exception as e:
                    print(f"Error processing image {path}: {e}")
                    continue

        if not valid_images:
            return False, "No valid images to convert"

        # Convert all processed images to PDF
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(valid_images))
            
        return True, output_path
    except Exception as e:
        return False, str(e)

def compress_image(image_path, output_path, quality=60, max_width=None):
    """
    Compresses an image by reducing quality and optionally resizing.
    """
    try:
        with Image.open(image_path) as img:
            # Handle transparency
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Resize if max_width is provided
            if max_width and img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(float(img.height) * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            img.save(output_path, format="JPEG", quality=quality, optimize=True)
            
        return True, output_path
    except Exception as e:
        return False, str(e)

def optimize_image(image_path, quality=85):
    """
    Optimizes an image for smaller PDF size.
    """
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(image_path, format="JPEG", quality=quality, optimize=True)
        return True
    except Exception as e:
        print(f"Optimization error: {e}")
        return False
