
# coding: utf-8

# In[ ]:


#requirements psutils
#gnome-terminal --full-screen on startup
import drive_utils
import termwriter 
import filelogger
import misc
import copier
from termwriter import *

import os
from termcolor import colored as col
from tqdm import tqdm
import shutil
import time
from datetime import datetime

if misc.jupyter_mode():
    tqdm.monitor_interval = 0
    get_ipython().run_line_magic('reload_ext', 'autoreload')
    get_ipython().run_line_magic('autoreload', '2')
    misc.save_jupyter_as_py('media-copier.ipynb')


# In[17]:


vid_ext = misc.get_video_ext()
poll = drive_utils.drivePollster()
events      = True #
copy_done   = False
countdown   = 1


for ii in range(1000):
    #--------------------------------------------------------
    #Triggers: when devices are plugged in/out
    if poll.did_change() or ii==0: 
        copy_done = False
        start = time.time()
        
        drives = drive_utils.get_drives()
        max_usb = None

        #Use largest USB harddrive
        for drive in drives:
            if drive_utils.is_usb_drive(drive.device):
                if max_usb is None:
                    max_usb = drive
                elif drive.size_total > max_usb.size_total:
                    max_usb = drive

        #Use others as SSD
        ssd = None
        for i in drives:
            if (drive_utils.is_usb_drive(i.device)
                and not i==max_usb):
                
                ssd = i
    
    
    #--------------------------------------------------------
    # Crude color display
    termwriter.cls()
    cols, lines = shutil.get_terminal_size((80, 20))
    if not (max_usb and ssd):
        printterm(col('+'+"-"*(cols-2)+'+', "red"))
        printterm(col(pline('', '|','|'), "red"))

        printterm(
            (col('| Please insert ', 'red') + 
             col('USB Hard drive ', 'cyan') + 
             col('and ', 'red') + 
             col('camera SSD ', 'green') +
             col('-\|/'[ii%4], 'red') +
             ' '*cols
            )[:cols+9*5-1] + col('|', 'red')
        )

        printterm(col(pline('', '|','|'), "red"))
        printterm(col('+'+"-"*(cols-2)+'+', "red"))

    else:
        #--------------------------------------------------------
        # Copy from SSD to hard-drive
        printterm(col('+'+"-"*(cols-2)+'+', "green"))
        printterm(col(pline(' ---- Copy from: ----', '|','|'), "green"))
        printterm(col(pline('   '+ssd.mountpoint, '|','|'), "green"))
        printterm(col(pline("    free:  %d GB"% (ssd.size_free //(2**30)), '|','|'), 'green'))
        printterm(col(pline("    total: %d GB"%(ssd.size_total//(2**30)), '|','|'), 'green'))
        printterm(col('+'+"-"*(cols-2)+'+', "green"))
        
        #printterm(col('+'+"-"*(cols-2)+'+', "cyan"))
        printterm(col(pline(' ---- Copy to: ----', '|','|'), "cyan"))
        printterm(col(pline('   '+max_usb.mountpoint, '|','|'), "cyan"))
        printterm(col(pline("     free:  %d GB"% (max_usb.size_free //(2**30)), '|','|'), 'cyan'))
        printterm(col(pline("     total: %d GB"%(max_usb.size_total//(2**30)), '|','|'), 'cyan'))
        printterm(col('+'+"-"*(cols-2)+'+', "cyan"))
        
        
        #Do not copy if the routine is already finished
        if copy_done:
            printterm()
            printterm("SD card backup is complete!")
            printterm("You may remove devices...")
            continue
        
        #--------------------------------------------------------
        # Wait 20 second
        printterm()
        if (time.time()-start) < countdown:
            printterm(' %d s left to cancel (plug out device)...'%(
                countdown - (time.time()-start)))
            continue
            
        #--------------------------------------------------------
        # Do the copy
        printterm(" Scanning files:")

        hdd_dir = os.path.join(max_usb.mountpoint, 'SD_autobackup')

        out_dir = os.path.join(hdd_dir,
                               datetime.now().strftime('%Y%m%d-')+
                               copier.get_valid_filename(ssd.id)+'--%.1fGB'%(
                                   ssd.size_total/(2**30)))


        os.makedirs(hdd_dir, exist_ok=True)

        fileregister = filelogger.get_fileregister(hdd_dir)
        newregister = {}


        t = tqdm(total=ssd.size_used, file=sysout, unit='B', unit_scale=True)
        sd_base = os.path.abspath(ssd.mountpoint)
        totsize = 0
        filecount = misc.dotdict(files=0, size=0, vidfiles=0, vidsize=0)
        for _, dirs, files in os.walk(sd_base, followlinks=False):
            for file in files:
                fpath = os.path.join(_, file)
                try:
                    key, attrs = filelogger.to_register(fpath)
                except FileNotFoundError:
                    pass
                    #print('File not found ', fpath)
                else:
                    if key not in fileregister:
                        newregister[key] = attrs

                        filecount.files += 1
                        filecount.size  += attrs.size
                        if os.path.splitext(attrs.path)[-1] in vid_ext:
                            filecount.vidfiles += 1
                            filecount.vidsize  += attrs.size

                t.update(attrs.size/2**30)
        t.close()
        printterm('\r', end='')

        printterm('Uncopied videos %.2fGB; %d files.'%(filecount.vidsize/2**30, filecount.vidfiles))
        printterm('Uncopied others %.2fGB; %d files)'%(filecount.size/2**30, filecount.files))
        printterm()

        i=0
        t = tqdm(total=filecount.size, file=sysout, unit='B', unit_scale=True)
        for key, attrs in newregister.items():
            i+=1

            src = attrs.path
            #TODO: for some f*** reason os.path.join doesn't work here ???
            # think it happens with files starting with a dot
            dest = os.path.abspath(out_dir +'/'+src[len(sd_base):])
            dest_dir = os.path.dirname(dest)

            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)

            keeps = misc.dotdict()
            for chunksz in copier.copy_with_progress(src, dest, keeps=keeps):
                t.update(chunksz)

            #shutil.copy2(src, dest)
            #t.update(attrs.size)

            if copier.hash_equals(keeps.md5, copier.hash_file(dest)):
                filelogger.update_fileregister(hdd_dir, attrs)
                
                
            #else:
            #    print('biiiiig problems', src, dest)

        t.close()
        printterm('\r', end='')
        
        copy_done = True

        
    time.sleep(0.5)

