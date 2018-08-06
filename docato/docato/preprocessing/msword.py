import subprocess, pdf, tempfile, logging, html, os
from django.conf import settings

logger = logging.getLogger('preprocessing')

def parse(filename, window_width = 1000):
    try:
        with tempfile.NamedTemporaryFile(delete = False) as f:
            tmp_fname = f.name
            subprocess.check_call([settings.TIKA_PREFIX + 'tika', '--encoding=utf-8', '--html', filename],
                                  stdout = f)
        return html.parse(tmp_fname, window_width)
    except subprocess.CalledProcessError as err:
        logger.warning('Could not convert MSOffice file "%s" using tika because of %s, trying unoconv...' % (filename, err))
        try:
            subprocess.check_call(['unoconv', '-fpdf', '-o', tmp_fname, filename])
            return pdf.parse(tmp_fname, window_width)
        except subprocess.CalledProcessError as err:
            logger.error('Could not convert MSOffice file "%s" using unoconv because of %s' % (filename, err))
            raise PreprocError()
    finally:
        if tmp_fname and os.path.exists(tmp_fname):
            os.remove(tmp_fname)
