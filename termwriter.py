"""Tips and tricks for writing to the terminal. We add functionality
as needed.
"""

import misc
import os
import shutil
    
debug = misc.jupyter_mode()
sysout = open('/dev/stdout', 'w')


coldict = misc.dotdict(
    RED = '\033[31m',
    GREEN = '\033[32m',
    BLUE = '\033[34m',
    MAGT  = '\033[35m',
    CYAN  = '\033[36m',
    WHITE = '\033[36m',

    REDB = '\033[101m',
    GREENB = '\033[102m',
    BLUEB = '\033[104m',
    MAGTB = '\033[105m',
    CYANB = '\033[106m', 
    
    END = '\033[0m',
    BOLD = '\033[1m',
    ULINE = '\033[4m',
)
colset = {i for i in coldict.values()}

def printterm(*args, **kwargs):
    """Wrapper for print in order to print to /dev/stdout and not sys.stdout.
    We use this to write to the console from a jupyter instance.
    """
    print(*args, file=sysout, **kwargs)
    
def line_idxes(line):
    r"""Find the character indexes in a string without color info mixed in 
    between
    
    Parameters
    ----------
    line: str
        The input string like "Hi \033[34mDoggy\033[0m"
            
    Examples
    --------
    >>> line = "Hi \033[34mDoggy\033[0m"
    >>> idxes, end = line_idxes(line)
    >>> ''.join([line[i] for i in idxes])
    'Hi Doggy'
    >>> end
    13
    >>> len(idxes)
    8
    """
    
    line_flat = line
    for col in colset:
        line_flat = line_flat.replace(col,'')
    
    idxes = []
    lead = 0
    end = 0
    for i in range(len(line_flat)):        
        if line[i+lead] == '\033':
            for col in colset:
                if line[i+lead:i+lead+len(col)] == col:
                    lead+=len(col)
                    end+=len(col)
        end+=1
        idxes.append(lead+i)
        
    return idxes, end

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
    
    colms, lines = shutil.get_terminal_size((80, 20))
    
    line = lpad+txt+' '*colms
    lidx, _ = line_idxes(line)
    ridx, _ = line_idxes(rpad)
    
    lend = lidx[colms-len(ridx)]
    line = line[:lend] +rpad
    
    return line

def writeterm(line, lpad='', rpad=''):
    """Write non-wrappable lines to the terminal
    """
    for i in line.split('\n'):
        printterm(pline(i, lpad=lpad, rpad=rpad))
    

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