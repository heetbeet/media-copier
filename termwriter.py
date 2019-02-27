"""Tips and tricks for writing to the terminal. We add functionality
as needed.
"""

import misc
import os
import shutil
    
debug = misc.jupyter_mode()
sysout = open('/dev/stdout', 'w')

def printterm(*args, **kwargs):
    """Wrapper for print in order to print to /dev/stdout and not sys.stdout.
    We use this to write to the console from a jupyter instance.
    """
    print(*args, file=sysout, **kwargs)


def pline(txt, lpad='', rpad=''):
    """Ensure the text doesn't wrap over console width.
    
    Parameters
    ----------
    txt: str
        Input text of any length. Truncate or space-pad this text to the 
        size of the terminal width (minus `lpad` width and `rpad` width).
    lpad: str, optional
        Pad the left with something like lpad='|' for '|My input text    ' 
    rpad: str, optional
        Pad the right with something like rpad='|' for 'My input text   |' 
        
    Examples
    --------
    >>> line = pline('Hello World', lpad='|', rpad='|')
    >>> line.startswith('|Hello')
    True
    >>> line.endswith('|')
    True
    """
    
    cols, lines = shutil.get_terminal_size((80, 20))
    canvas = [' ']*cols
    
    canvas[:len(lpad)] = [i for i in lpad]
    canvas[cols-len(rpad): ] = [i for i in rpad]
    
    N = len(canvas[len(lpad):len(rpad)+len(txt)])
    canvas[len(lpad):len(rpad)+len(txt)] = [i for i in txt[:N]]

    return ''.join(canvas)


def cls():
    """Clears the terminal screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    if debug:
        from IPython.display import clear_output
        clear_output()

        
if __name__ == "__main__":
    import termwriter
    import doctest
    doctest.testmod()