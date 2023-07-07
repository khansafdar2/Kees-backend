
from io import BytesIO
from django.http import HttpResponse
from authentication.models import EmailTemplates
from xhtml2pdf import pisa


def render_to_pdf(context_dict=None):
    if context_dict is None:
        context_dict = {}

    templates = EmailTemplates.objects.filter(title='order_invoice').first()
    template_content = templates.template

    for key, value in context_dict.items():
        key = '{{' + key + '}}'
        template_content = template_content.replace(key, str(value))

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(template_content.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

