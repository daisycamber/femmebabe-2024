def highlight_code(code):
    from pygments import highlight
    from pygments.lexers import PythonLexer, BashLexer, BashSessionLexer
    from pygments.formatters import HtmlFormatter
    return highlight(code, PythonLexer(), HtmlFormatter())

def highlight_shell(code):
    from pygments import highlight
    from pygments.lexers import PythonLexer, BashLexer, BashSessionLexer
    from pygments.formatters import HtmlFormatter
    return highlight(code, BashSessionLexer(), HtmlFormatter())
