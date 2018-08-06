import logging
import nltk.tokenize, lxml.html
from StringIO import StringIO

logger = logging.getLogger('preprocessing')


def align_text(plain_text, formatted_html):
    tokens = nltk.tokenize.wordpunct_tokenize(plain_text)
    tree = lxml.html.parse(StringIO(formatted_html))
    align_node(tree.xpath('/html/body')[0], tokens, 0, 0, 0)
    result = lxml.html.tostring(tree)
#     with open('/tmp/2222222.html', 'w') as f:
#             f.write(result)
    return result


def align_node(node, tokens, cur_token_i, cur_tok_char_i, cur_global_char_i):
    original_children = node.getchildren()
    # logger.debug('align_node %r' % ((cur_token_i, cur_tok_char_i, cur_global_char_i),))
    if node.text and node.text.strip():
        # logger.debug('Aligning text %r' % node.text)
        unmatched_prefix, cur_token_i, cur_tok_char_i, cur_global_char_i, pref_nodes = align_plain_text(node,
                                                                                                        node.text,
                                                                                                        tokens,
                                                                                                        cur_token_i,
                                                                                                        cur_tok_char_i,
                                                                                                        cur_global_char_i)
        node.text = unmatched_prefix
        # logger.debug('Unmatched prefix %r' % node.text)
        for i, n in enumerate(pref_nodes):
            node.insert(i, n)

    if original_children:
        # logger.debug('Aligning children...')
        for chnode in original_children:
            cur_token_i, cur_tok_char_i, cur_global_char_i = align_node(chnode,
                                                                        tokens,
                                                                        cur_token_i,
                                                                        cur_tok_char_i,
                                                                        cur_global_char_i)
        # logger.debug('Back to parent')

    if node.tail:
        # logger.debug('Aligning tail %r' % node.tail)
        unmatched_prefix, cur_token_i, cur_tok_char_i, cur_global_char_i, suf_nodes = align_plain_text(node,
                                                                                                       node.tail,
                                                                                                       tokens,
                                                                                                       cur_token_i,
                                                                                                       cur_tok_char_i,
                                                                                                       cur_global_char_i)
        node.tail = u''
        for n in reversed(suf_nodes):
            node.addnext(n)
        node.tail = unmatched_prefix
        # logger.debug('Unmatched tail %r' % node.tail)
    return cur_token_i, cur_tok_char_i, cur_global_char_i


def align_plain_text(some_node, text_to_mark, tokens, cur_token_i, cur_tok_char_i, cur_global_char_i):
    # logger.debug('align_plain_text %r' % ((text_to_mark, cur_token_i, cur_tok_char_i, cur_global_char_i),))

    if cur_token_i >= len(tokens):
        # logger.debug('Beyond tokens array')
        return text_to_mark, cur_token_i, cur_tok_char_i, cur_global_char_i, []

    cur_token = tokens[cur_token_i]
    cur_char = cur_token[cur_tok_char_i]
    new_children = []

    last_chunk = None
    last_matched_text = u''
    first_matched_char = text_to_mark.find(cur_char)
    if first_matched_char >= 0:
        unmatched_prefix = text_to_mark[:first_matched_char]
        text_to_mark = text_to_mark[first_matched_char:]
        for ch in text_to_mark:
            if ch == cur_char:
                last_matched_text += ch
                cur_global_char_i += 1
                if cur_tok_char_i == len(cur_token) - 1:
                    start_char_id = str(cur_global_char_i - len(last_matched_text))
                    last_chunk = some_node.makeelement('span',
                                                       attrib={
                                                                 'id' : 'chunk_%s' % start_char_id,
                                                                 'class' : 'chunk token_%i' % cur_token_i,
                                                                 'data-token-id' : str(cur_token_i),
                                                                 'data-global-char-id' : start_char_id
                                                                 })
                    last_chunk.text = last_matched_text
                    # logger.debug('matched chunk %r' % ((last_chunk.text, start_char_id, cur_token_i),))
                    last_matched_text = u''
                    new_children.append(last_chunk)
                    cur_token_i += 1
                    cur_tok_char_i = 0
                    if cur_token_i < len(tokens):
                        cur_token = tokens[cur_token_i]
                else:
                    cur_tok_char_i += 1
                cur_char = cur_token[cur_tok_char_i]
            else:
                if last_chunk is not None:
                    if not last_chunk.tail:
                        last_chunk.tail = u''
                    last_chunk.tail += ch
                    # logger.debug('Appened %r to the last chunk tail %r' % (ch, last_chunk.tail))
                    
        if last_matched_text:
            start_char_id = str(cur_global_char_i - len(last_matched_text))
            last_chunk = some_node.makeelement('span',
                                               attrib={
                                                         'id' : 'chunk_%s' % start_char_id,
                                                         'class' : 'chunk token_%i' % cur_token_i,
                                                         'data-token-id' : str(cur_token_i),
                                                         'data-global-char-id' : start_char_id
                                                         })
            last_chunk.text = last_matched_text
            # logger.debug('matched the rest of string: %r' % ((last_chunk.text, start_char_id, cur_token_i),))
            new_children.append(last_chunk)
    else:
        unmatched_prefix = text_to_mark
    result = (unmatched_prefix, cur_token_i, cur_tok_char_i, cur_global_char_i, new_children)
    # logger.debug('align_plain_text result: %r' % (result,))
    return result
