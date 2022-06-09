# Module waitforwindow waits for a window with a specific window class and/or window name to be displayed

import time
import win32gui
import win32con
from optparse import OptionParser


def readCommandLineParameters():
    '''
    Read command line parameters
    '''
    parser = OptionParser()
    
    parser.add_option("-c", "-C", help = "Window Class Name of window to wait for (optional)")
    parser.add_option("-n", "-N", help = "Window Name (Caption) of window to wait for (optional)")
    parser.add_option("-t", "-T", help = "Timeout in seconds (optional). Default value: 300 seconds")
    # Parse the command line
    (opts, args) = parser.parse_args()
    # Return the options as a dictionary of option:value
    return vars(opts)


def waitForWindow(windowclassname, windowname, timeout):
    sleeptime = 0.1
    iterations = 0
    while sleeptime * iterations < timeout:
        hwnd = win32gui.FindWindow(windowclassname, windowname)
        if hwnd != 0:
            return hwnd
        else:
            time.sleep(sleeptime)
            iterations += 1
    return -1

def findAndHideWindow(name, timeout):
    hwnd = waitForWindow(name, timeout)
    if hwnd:
        # Sleep for a short while to let the window be created properly
        time.sleep(1)
        # Hide the window
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
       
       
def main():
    timeout = 300
    params = readCommandLineParameters()
    if params['c'] is None and params['n'] is None:
        print "ERROR: You must specify Window Class Name or Window Name!"
        return 0
    windowclassname = params['c']
    windowname = params['n']
    if params['t'] is not None:
        timeout = int(params["t"])
    
    print "Now waiting for window with Window Class Name=%s, Window Name=%s. Timeout=%i seconds..." %(windowclassname, windowname, timeout)
    #hwnd = waitForWindow(windowclassname, windowname, timeout)
    hwnd = waitForWindow(windowclassname, windowname, timeout)
    return hwnd
        
           
if __name__=='__main__':
    main()

