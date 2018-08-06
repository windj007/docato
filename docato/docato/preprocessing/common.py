import re, lxml.html, StringIO

class PreprocError(Exception):
    pass

_WORD_DIV_RE = re.compile(r'([^\W\d_]+)-\n\s*([^\W\d_]+)', re.I | re.U)
_WORD_DIV_SUB = r'\1\2'
def remove_word_divisions(text):
    return _WORD_DIV_RE.sub(_WORD_DIV_SUB, text)

def parse_html(converted_content):
    return lxml.html.parse(StringIO.StringIO(converted_content))


def get_tokens_from_parsed(tree):
    chunks = tree.xpath('.//span[contains(@class, "chunk")]')
    chunks.sort(key = lambda c: int(c.get("data-global-char-id")))
    cur_token_i = None
    cur_token_start = None
    cur_token_text = ""
    for chunk in chunks:
        chunk_token_i = int(chunk.get("data-token-id"))
        if cur_token_i == chunk_token_i:
            cur_token_text += chunk.text
        else:
            if len(cur_token_text) > 0:
                yield {
                       'text' : cur_token_text,
                       'seq_no' : cur_token_i,
                       'start' : cur_token_start,
                       'end' : cur_token_start + len(cur_token_text)
                       }
            cur_token_i = chunk_token_i
            cur_token_text = chunk.text
            cur_token_start = int(chunk.get("data-global-char-id"))


def get_text_and_tokens_from_parsed(tree):
    tokens = list(get_tokens_from_parsed(tree))
    if not tokens:
        return '', tokens
    tokens.sort(key = lambda t: t['seq_no'])
    result = ''
    prev_end = tokens[0]['start']
    for t in tokens:
        result += (' ' * (t['start'] - prev_end + 1)) + t['text']
        prev_end = t['end']
    return result, tokens


def get_grouped_tokens_from_parsed(tree):
    result = collections.defaultdict(list)
    for token in get_tokens_from_parsed(tree):
        result[token['text'].lower()].append({
                                              'seq_no' : token['seq_no'],
                                              'start' : token['start'],
                                              'end' : token['end']
                                              })
    return result


def get_doc_tokens(doc):
    tree = lxml.html.parse(StringIO.StringIO(doc.converted_content))
    return get_grouped_tokens_from_parsed(tree)

def get_doc_text_and_tokens(doc):
    tree = lxml.html.parse(StringIO.StringIO(doc.converted_content))
    return get_text_and_tokens_from_parsed(tree)


def get_tokens_range(tree):
    token_ids = map(int, set(tree.xpath('.//span[contains(@class, "chunk")]/@data-token-id')))
    return (min(token_ids), max(token_ids))


def get_tokens_from_str(converted_content):
    return get_tokens_from_parsed(parse_html(converted_content))


_SPECIAL_REGEX_CHARACTERS = frozenset(r'\[]().+*?$^')
def make_token_matcher_regex(token):
    result = ''
    for c in token:
        if result:
            result += r'[\-\s]*'
        if c in _SPECIAL_REGEX_CHARACTERS:
            result += '\\'
        result += c
    return result

def get_next_token_pos(text, token, start_pos):
    assert len(token) > 0
    if len(token) == 1:
        return text.find(token, start_pos)
    else:
        match = re.search(make_token_matcher_regex(token), text[start_pos:])
        return (match.start() + start_pos) if match else -1

def align_tokens_to_text(text, tokens):
    # print len(text)
    cur_position = 0
    for i, t in enumerate(tokens):
        #print 'cur_position1', cur_position
        t_pos = get_next_token_pos(text, t['text'], cur_position)
        #print t_pos
        assert t_pos >= 0, (cur_position, t, ' '.join(t['text'] for t in tokens[i - 10:i]), text[cur_position - 40 : cur_position + 20])
        if t_pos - cur_position > len(t) * 2:
            continue
            #print 'too far', (cur_position, t, ' '.join(t['text'] for t in tokens[i - 10:i]), text[cur_position - 40 : cur_position + 20])
        else:
            this_token = dict(t)
            this_token['start'] = t_pos
            this_token['end'] = t_pos + len(this_token['text'])
            #print 'matched', (cur_position, this_token, ' '.join(t['text'] for t in tokens[i - 10:i]), text[cur_position - 40 : cur_position + 20])
            yield this_token
            cur_position = this_token['end']
#        print

