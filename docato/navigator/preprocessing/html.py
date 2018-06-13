import tempfile, os, logging, shutil, subprocess, traceback
import pdf
from BeautifulSoup import UnicodeDammit


logger = logging.getLogger('preprocessing')


def parse(filename, window_width = 1000):
    logger.info('Got HTML to parse: %s' % filename)
    try:
        with tempfile.NamedTemporaryFile(suffix = '.html', delete = False) as f:
            copy_fname = f.name
        with tempfile.NamedTemporaryFile(delete = False) as f:
            conv_fname = f.name
        shutil.copy2(filename, copy_fname)
        # try to determine encoding and decode
        with open(copy_fname, 'rb') as f:
            converted = UnicodeDammit(f.read(), isHTML = True)
        if converted.unicode:
            with open(copy_fname, 'wb') as f:
                f.write(converted.unicode.encode('utf8'))
        args = ['wkhtmltopdf', '--encoding', 'utf-8', copy_fname, conv_fname]
        env = { 'DISPLAY' : ':99' }
        logger.debug('Calling wkhtmltopdf with arguments %r' % args)
        subprocess.check_call(args, env = env)
        logger.debug('Wkhtmltopdf has done the job')
        return pdf.parse(conv_fname, window_width)
    except subprocess.CalledProcessError as err:
        logger.error('wkhtmltopdf failed to convert "%s" because of %s\n%s' % (filename, err, traceback.format_exc()))
        raise PreprocError()
    finally:
        if copy_fname and os.path.exists(copy_fname):
            os.remove(copy_fname)
        if conv_fname and os.path.exists(conv_fname):
            os.remove(conv_fname)
