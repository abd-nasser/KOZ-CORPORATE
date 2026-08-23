import os
import io
from django.conf import settings
from django.template.loader import get_template
from django.contrib.staticfiles import finders
from xhtml2pdf import pisa

def link_callback(uri, rel):
    """
    Convertit les URIs /static/ ou /media/ en chemins absolus du système de fichiers.
    """
    s_url = settings.STATIC_URL  # Ex: '/static/'
    m_url = settings.MEDIA_URL   # Ex: '/media/'

    path = None

    # 1. Gestion des fichiers STATIC
    if uri.startswith(s_url):
        # On retire le préfixe '/static/' -> 'images/Koz_logo_noBack.png'
        relative_path = uri[len(s_url):]
        # On cherche dans les STATICFILES_DIRS / apps
        path = finders.find(relative_path)
        
        # Fallback si STATIC_ROOT est utilisé en prod
        if not path and getattr(settings, 'STATIC_ROOT', None):
            path = os.path.join(settings.STATIC_ROOT, relative_path)

    # 2. Gestion des fichiers MEDIA
    elif m_url and uri.startswith(m_url):
        relative_path = uri[len(m_url):]
        if getattr(settings, 'MEDIA_ROOT', None):
            path = os.path.join(settings.MEDIA_ROOT, relative_path)

    # 3. Fallback direct avec finders
    else:
        path = finders.find(uri)

    # Si un chemin valide est trouvé, on retourne le chemin absolu normalisé
    if path:
        if isinstance(path, (list, tuple)):
            path = path[0]
        return os.path.abspath(path)

    return uri

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    
    pdf = pisa.pisaDocument(
        io.BytesIO(html.encode("UTF-8")), 
        result,
        link_callback=link_callback
    )
    
    if not pdf.err:
        return result.getvalue()
    return None