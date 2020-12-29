from IPython.core.magic import (Magics, magics_class, line_magic)
from notifyg import service

@magics_class
class NotifyMagics(Magics):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = None

    @line_magic
    def notifyg_init(self, line):
        self.source = service.Source(name=line)
        print(self.source.register_url)
        return line

    @line_magic
    def notifyg(self, line):
        if self.source is None:
            raise ValueError('Not initialized. Use %notifyg_init first')
        self.source.send(line)
        return line