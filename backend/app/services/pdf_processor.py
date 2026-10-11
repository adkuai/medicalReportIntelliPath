import io
import base64
from typing import Tuple, List
from PIL import Image

try:
    import pypdfium2 as pdfium
except ImportError:
    pdfium = None

class PDFProcessor:
    @staticmethod
    def process_uploaded_bytes(file_bytes: bytes, filename: str) -> Tuple[List[str], str]:
        """
        Converts uploaded file (PDF or Image) into a list of base64-encoded JPEG image strings.
        Returns:
            Tuple: (list_of_base64_images, detected_mime_type)
        """
        lower_name = filename.lower()
        base64_images = []

        if lower_name.endswith(".pdf") or file_bytes.startswith(b"%PDF"):
            if pdfium is None:
                raise RuntimeError("pypdfium2 is not installed. Please install pypdfium2 to handle PDF documents.")
            
            # Load PDF using pypdfium2
            pdf = pdfium.PdfDocument(file_bytes)
            num_pages = len(pdf)
            # Process up to 3 pages for medical multi-page reports to stay within model token bounds
            pages_to_render = min(num_pages, 3)

            for i in range(pages_to_render):
                page = pdf[i]
                # Render at 2.0 scale (144 DPI) for sharp, clear handwriting & lab numbers
                bitmap = page.render(scale=2.0)
                pil_image = bitmap.to_pil()

                # Convert to RGB if needed
                if pil_image.mode != "RGB":
                    pil_image = pil_image.convert("RGB")

                buffer = io.BytesIO()
                pil_image.save(buffer, format="JPEG", quality=92)
                b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
                base64_images.append(b64_str)

            return base64_images, "application/pdf"

        else:
            # Standard image formats (JPEG, PNG, WEBP, TIFF, BMP)
            image = Image.open(io.BytesIO(file_bytes))
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Resize if unnecessarily large (e.g. > 2800px on longest side) to optimize inference speed
            max_dimension = 2400
            if max(image.size) > max_dimension:
                image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=90)
            b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            base64_images.append(b64_str)

            return base64_images, "image/jpeg"

