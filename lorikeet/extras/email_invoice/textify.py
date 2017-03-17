from html import parser

BLOCK_ELEMENTS = ('address', 'article', 'aside', 'blockquote', 'br',
                  'canvas', 'dd', 'div', 'dl', 'fieldset', 'figcaption',
                  'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4',
                  'h5', 'h6', 'header', 'hgroup', 'hr', 'li', 'main',
                  'nav', 'noscript', 'ol', 'output', 'p', 'pre',
                  'section', 'table', 'tfoot', 'ul', 'video')


class TextifyParser(parser.HTMLParser):
    element_stack = []

    def __init__(self, transformer):
        super().__init__()
        self.transformer = transformer
        self.element_stack = [('DOCUMENT', (), [])]

    def handle_starttag(self, tag, attrs):
        attr_dict = {k: v for (k, v) in attrs}
        self.element_stack.append((tag, attr_dict, []))

    def handle_endtag(self, tag):
        last_element = self.element_stack.pop()
        transformed_element = self.transformer(*last_element)
        self.handle_data(transformed_element)

    def handle_data(self, data):
        self.element_stack[-1][2].append(data)

    def get_result(self):
        return self.element_stack[0][2]

    def get_string_result(self):
        return ''.join(self.get_result())


def transformer(name, attrs, body_list):
    body = ''.join(body_list)

    if name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        return body + '\n' + '=' * len(body) + '\n'
    if name == 'a' and 'href' in attrs:
        return body + ' [' + attrs['href'] + ']'

    if name in BLOCK_ELEMENTS:
        return body + '\n'
    else:
        return body


def transform(input):
    parser = TextifyParser(transformer)
    parser.feed(input)
    return parser.get_string_result()
