import logging
import pdf, html, txt, msword, align
 
logger = logging.getLogger('preprocessing')

class PreprocError(Exception):
    pass


PDF_EXTENSION = 'pdf'
HTML_EXTENSIONS = frozenset(['htm', 'html', 'xhtml'])
TXT_EXTENSIONS = frozenset(['ksh', 'txt'])
MSOFFICE_EXTENSIONS = frozenset(['doc', 'docx', 'rtf', 'ppt', 'pptx', 'dot', 'dotx'])
def get_preprocessor_by_extension(ext):
    if ext == PDF_EXTENSION:
        return pdf
    if ext in HTML_EXTENSIONS:
        return html
    if ext in TXT_EXTENSIONS:
        return txt
    if ext in MSOFFICE_EXTENSIONS:
        return msword
    logger.error('Files of type %s are not supported yet' % ext)
    raise PreprocError()