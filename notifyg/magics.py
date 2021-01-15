import ast
import io
import traceback
import sys
import six
from IPython.core.magic import (Magics, magics_class, line_magic, line_cell_magic, needs_local_scope)
import qrcode
from notifyg import service

@magics_class
class NotifyMagics(Magics):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = None

    @line_magic
    def notifyg_init(self, line):
        self.source = service.Source(name=line)
        print('Open the following link to configure this notification channel.')
        print(self.source.register_url)
        return qrcode.make(self.source.register_url)

    @needs_local_scope
    @line_cell_magic
    def notifyg(self, line='', cell=None, local_ns=None):
        if self.source is None:
            raise ValueError('Not initialized. Use %notifyg_init first')
        if line and cell:
            raise ValueError("Can't use statement directly after '%%notifyg'!")
        if cell:
            expr = self.shell.input_transformer_manager.transform_cell(cell)
        else:
            expr = self.shell.input_transformer_manager.transform_cell(line)
        expr_ast = self.shell.compile.ast_parse(expr)
        expr_ast = self.shell.transform_ast(expr_ast)
        eval_expr_ast = None
        exec_expr_ast = None
        if len(expr_ast.body) == 1 and isinstance(expr_ast.body[0], ast.Expr):
            eval_expr_ast = ast.Expression(expr_ast.body[0].value)
        elif len(expr_ast.body) > 0 and isinstance(expr_ast.body[-1], ast.Expr):
            eval_expr_ast = ast.Expression(expr_ast.body[-1].value)
            exec_expr_ast = ast.Module(body=expr_ast.body[:-1])
        else:
            exec_expr_ast = expr_ast
        source = '<notifyg>'
        cellresult = None
        try:
            if exec_expr_ast:
                exec(self.shell.compile(exec_expr_ast, source, 'exec'), self.shell.user_ns, local_ns)
            if eval_expr_ast:
                cellresult = eval(self.shell.compile(eval_expr_ast, source, 'eval'), self.shell.user_ns, local_ns)
                r = cellresult
            else:
                r = '(executed)'
        except:
            strio = io.StringIO()
            traceback.print_exc(file=strio)
            r = strio.getvalue()
            print(r, file=sys.stderr)
        image, mime_type = self._get_image(r)
        if image is not None:
            self.source.send_image(image, mime_type=mime_type)
        else:
            self.source.send(self._normalize(r))
        return cellresult

    def _get_image(self, value):
        if hasattr(value, 'data') and hasattr(value, 'format'):
            return io.BytesIO(value.data), 'image/' + value.format
        return None, None

    def _normalize(self, message):
        if isinstance(message, six.string_types):
            return message
        elif hasattr(message, 'read'):
            return message.read()
        return str(message)


def load_ipython_extension(ipython):
    '''
    Define %notifyg_init, %notify magic
    '''
    ipython.register_magics(NotifyMagics)
