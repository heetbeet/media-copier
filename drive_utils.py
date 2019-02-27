import os
import shutil
import psutil
from misc import systxt, dotdict

def is_usb_drive(sbx):
    """Test if a drive is connected via USB.
    
    Examples
    --------
    >>> is_usb_drive('/dev/sdb2')
    False
    
    """
    
    if '/' in sbx:
        sbx = sbx.split('/')[-1]
    str_out = systxt(['find', '/dev/disk/by-id/', '-lname', '*'+sbx])
    return len([i for i in str_out.replace('/',' ').split() if i.startswith('usb-')]) > 0 


def drive_id(sbx):
    """Get the ID of a drive.
    
    Examples
    --------
    >>> drive_id('/dev/sdb2') is not 'none'
    True
    
    """
    
    str_out = systxt(['udevadm', 'info', '--query=all', '--name='+sbx])
    str_out = str_out.split('ID_SERIAL=')
    if len(str_out)==1:
        return 'none'
    else:
        return str_out[1].split('\n')[0].strip()
    
        
def get_drives(exclude_mount=['/']):
    """Get a list of all drives on the system.
    
    Examples
    --------
    >>> sdb2 = None
    >>> for i in get_drives([]):
    ...     if i.device == '/dev/sdb2':
    ...         sdb2 = i
    >>> sdb2.mountpoint
    '/'
    >>> keys = list(sdb2.keys())
    >>> keys.sort()
    >>> keys
    ['device', 'fstype', 'id', 'mountpoint', 'opts', 'size_free', 'size_total', 'size_used']
    
    """
    drives = []
    for p in psutil.disk_partitions():
        if p.mountpoint in exclude_mount:
            continue
        #if is_usb_harddrive(p.device):
        p = dotdict(**p._asdict())
        (p.size_total, 
         p.size_used,
         p.size_free ) = shutil.disk_usage(p.mountpoint)
        p.id = drive_id(p.device)
        
        drives.append(p)
        
    return drives

class drivePollster:    
    """Returns a function that eveluates as True if a drive was plugged in
    or plugged out since the last check.
    
    Examples
    --------
    >>> import time
    >>> pollster = drivePollster()
    >>> ch = pollster.did_change() #maybe True
    >>> ch = pollster.did_change() #now False
    >>> ch
    False
    """
    def __init__(self):
        import select
        self.f = open('/proc/self/mounts')
        self.pollster = select.poll()
        self.pollster.register(self.f, select.POLLERR | select.POLLPRI)

    def did_change(self):
        return bool(self.pollster.poll(128))

    
if __name__ == "__main__":
    import drive_utils
    import doctest
    doctest.testmod()