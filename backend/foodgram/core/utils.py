import io

from django.http import response
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from core.services import get_subscription_ingredients


def draw_pdf_report(request):
    """Рисуем отчёт о предстоящих покупках в виде PDF-файла."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('FreeSans', 'api/FreeSans.ttf'))
    p.setFont('FreeSans', 14)
    p.drawCentredString(
        300, 800,
        'Ваш список покупок:')
    text_object = p.beginText(2 * cm, 29.7 * cm - 2 * cm)
    for line in get_subscription_ingredients(request).splitlines(False):
        text_object.textLine(line.rstrip())
    p.drawText(text_object)
    p.showPage()
    p.save()
    buffer.seek(0)
    return response.FileResponse(buffer, as_attachment=True,
                                 filename='shopping_list.pdf')
