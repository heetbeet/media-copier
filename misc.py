import subprocess
import os

class dotdict(dict):    
    """A dot-able dictionary for easy access to items. Note stay clear from
    keys that clashes with dict internals like: copy, fromkeys,
    get, items, keys, pop, popitem, setdefault, update, and values.

    ...
    
    Examples
    --------
    >>> a = DotDict(val1=1)
    >>> a.val2 = 2
    >>> a
    {'val1': 1, 'val2': 2}
    >>> a['val1']
    1
    >>> a.val1
    1
    """
    def __init__(self, **kwds):
        self.update(kwds)
        self.__dict__ = self
        
def systxt(cmd, **kwargs):
    r"""Wrapper over subprocess.call; run a terminal command and get the 
    results as a string.
    
    Parameters
    ----------
    cmd : list, str
        The command to run. Command and args are in a list of string. If
        a single is give, subprocess.call are run with shell=True.
    **kwargs :
        These are passed on to subprocess.call
    
    Returns
    -------
    str
        The resulting command output.
        
    Examples
    --------
    >>> systxt('echo hello')
    'hello\n'
    >>> systxt(['echo', 'hello'])
    'hello\n'
    """
        
    if isinstance(cmd, str):
        return subprocess.check_output(cmd, shell=True, **kwargs).decode('utf-8')
    else:
        return subprocess.check_output(cmd, **kwargs).decode('utf-8')
        
        
def jupyter_mode():
    """Test to see if __file__ is not available; if so, we are likely using
    a Jupyter instance. This is for debugging purposes.
    """
    import __main__ as main
    return not hasattr(main, '__file__')


def get_video_ext():
    """A list of video file extensions updated from wikipedia.org/wiki/Video_file_format and
    wikipedia.org/wiki/Comparison_of_video_container_formats retrieved on 2019-02-27
    
    Returns
    -------
    set
        Video file extensions both with dots and without (".avi" and "avi")
        
    Examples
    --------
    >>> exts = get_video_ext()
    >>> 'mp4' in exts
    True
    >>> '.mp4' in exts
    True
    """
    
    vid_ext = {'3g2', '3gp', 'amv', 'asf', 'avi', 'divx', 'drc', 'evo', 'f4a', 'f4b',
               'f4p', 'f4v', 'flv', 'gif', 'gifv', 'ifo', 'm2p', 'm2ts', 'm2v', 'm4p',
               'm4v', 'mcf', 'mk3d', 'mka', 'mks', 'mkv', 'mng', 'mov', 'mp2', 'mp4',
               'mpe', 'mpeg', 'mpg', 'mpv', 'mts', 'mxf', 'nsv', 'ogg', 'ogv', 'ps',
               'qt', 'rm', 'rmvb', 'roq', 'svi', 'ts', 'vob', 'webm', 'wma', 'wmv', 
               'yuv' }
    
    for i in [i for i in vid_ext]: #noqa
        vid_ext.add('.'+i)
        
    return vid_ext

def save_jupyter_as_py(filename, outfilename=None):
    subprocess.call(['jupyter', 'nbconvert', '--to', 'script', filename])
    
    #if filename[-6:].lower() != '.ipynb':
    #    raise ValueError('Filename must end with .ipynb', filename)
        
    #if outfilename is None:
    #    outfilename = filename[:-6]+'.py'
    #    
    #try:
    #    os.remove(outfilename)
    #except: pass
    #os.rename(filename, outfilename)


if __name__ == "__main__":
    import misc
    import doctest
    doctest.testmod()