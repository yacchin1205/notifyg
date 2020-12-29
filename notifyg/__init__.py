from notifyg.magics import NotifyMagics

def load_ipython_extension(ipython):
    '''
    Define %notifyg_init, %notify magic
    '''
    ipython.register_magics(NotifyMagics)
