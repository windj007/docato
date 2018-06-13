import chardet, re

_TEMPLATE = u'''
<html>
<head>
    <meta charset="utf-8"> 
</head>
<body>
%(content)s
</body>
</html>
'''

def parse(filename, window_width = None):
    with open(filename, 'r') as f:
        plain_text = f.read()
    charset = chardet.detect(plain_text)['encoding']
    plain_text = plain_text.decode(charset)
    body_content = re.sub(u'\n', u'<br />', plain_text)
    return _TEMPLATE % { 'charset' : charset, 'content' : body_content }, plain_text