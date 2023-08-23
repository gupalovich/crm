import base64
from io import BytesIO

import qrcode
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.http import HttpRequest
from django.template.loader import render_to_string
from docxtpl import DocxTemplate
from qrcode.image.pil import PilImage
from weasyprint import HTML


def generate_qr_code(data: str) -> PilImage:
    qr = qrcode.QRCode(version=1, box_size=6, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    return qr_img


def convert_img_to_base64(img: PilImage) -> str:
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img


def html_to_pdf(
    request: HttpRequest, template_path: str, context: dict, css_paths: list[str] = None
) -> bytes:
    if isinstance(css_paths, str):
        css_paths = [css_paths]
    if css_paths is not None:
        css_paths = [find(path) for path in css_paths]

    template = render_to_string(template_path, context)
    pdf_file = HTML(string=template, base_url=request.build_absolute_uri()).write_pdf(stylesheets=css_paths)
    return pdf_file


def render_docx(template_path: str, context: dict) -> bytes:
    doc = DocxTemplate(str(settings.APPS_DIR / "documents/templates" / template_path))

    doc.render(context)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer
