import os
import re
import hashlib
import shutil
from misc import dotdict

def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    
    Parameters
    ----------
    s: str
        Filename with possible non-standard characters.
        
    Returns
    -------
    str
        Filename casted to standard filename character set.
    
    Examples
    --------
    >>> copier.get_valid_filename("jóhn's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '_')
    import unicodedata
    s = (unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')).decode('utf-8')
    return re.sub(r'(?u)[^-\w.]', '', s)

def hash_equals(hash1, hash2):
    """Test if two hashlib object have the same digest
    
    Parameters
    ----------
    hash1 : obj:hashlib
        Hash 1
    hash2 : obj:hashlib
        Hash 2
    
    Returns
    -------
    bool
        Are the hashes equal?
    """
    
    return hash1.digest() == hash2.digest()
    
def hash_file(filepath):
    """Return the md5 hash of a file as a hashlib object, calculated piece by piece.
    To get the actual hash value, use val.digest() or val.digest().decode('utf-8').
    
    Parameters
    ----------
    filepath : str
        File to hash.
    
    Returns
    -------
    hashlib object
        The md5 hash of the file.

    Examples
    --------
    >>> import hashlib
    >>> md5_1 = copier.hash_file(__file__)
    >>> md5_2 = hashlib.md5(open(__file__, 'rb').read())
    >>> md5_1.digest() == md5_2.digest()
    True
    """
    
    md5 = hashlib.md5()
    chunk_size  = 1024*1024
    chunk_size -= chunk_size%md5.block_size  #nearest div
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            md5.update(chunk)
    return md5


def copy_with_progress(src_file,
                       dest_file,
                       do_md5=True,
                       keeps=dotdict(src_size=None,
                                     dest_size=None, 
                                     md5=None)):
    """An iterator to copy src_file to dest_file and returning feedback on the
    number of bytes written. The idea is to use this in conjuction with a
    progress bar like tqdm. Note that the copy only progresses on every `next`.
    
    Parameters
    ----------
    src_file : str
        The file to copy.
    dest_file : str
        The location to copy src_file to.
    do_md5 : bool, optional
        Should a md5 hash of the src_file be calculated along the way?
    keeps : dotdict, optional
        A hacky way to find info after the iterator is done. Pass a dotdict
        then keeps.src_size (int), keeps.dest_size (int), and 
        keeps.md5 (hashlib.md5) will become available afterwards.

    Yields
    ------
    int
        Yields the size of the last chunk.

    Raises
    ------
    ValueError
        If src size != dest size..

    Examples
    --------
    >>> import tempfile
    >>> src_file = __file__
    >>> dst_file = os.path.join(tempfile.gettempdir(), 'tstcopier.py')
    
    >>> keeps = dotdict()
    >>> for chunk_sz in copier.copy_with_progress(
    ...                   src_file,
    ...                   dst_file,
    ...                   keeps=keeps):
    ...     pass
    >>> keeps.src_size == keeps.dest_size
    True
    >>> os.stat(dst_file).st_size == keeps.dest_size
    True
    >>> os.remove(dst_file)
    """
    
    chunk_size  = 1024*1024
    keeps.src_size = os.stat(src_file).st_size
    keeps.dest_size = 0
    
    if do_md5:
        keeps.md5 = hashlib.md5()
        chunk_size -= chunk_size%keeps.md5.block_size #nearest div

    with open(src_file, 'rb') as f_src:
        with open(dest_file, 'wb') as f_dest:
            data = f_src.read(chunk_size)
            while len(data):
                f_dest.write(data)
                keeps.dest_size += len(data)
                if do_md5:
                    keeps.md5.update(data)
                yield len(data)

                data = f_src.read(chunk_size)
    shutil.copystat(src_file, dest_file)
    
    if  keeps.dest_size != keeps.src_size:
        ValueError('File copy incomplete, src size != dest size.')
        

if __name__ == "__main__":
    import copier
    import doctest
    doctest.testmod()
