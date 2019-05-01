
try:
    import socket
except:
    print('Please check your Python installation, socket module is not present. \n')

try:
    from tkinter import *
except:
    print('Please check your Python installation, tkinter module is not present. \n')

try:
    from tkinter import filedialog
except:
    print('Please check your Python installation, tkinter module is not present. \n')


try:
    from tkinter import ttk
except:
    print('Please check your Python installation, tkinter (ttk) module is not present. \n')


try:
    from ttkthemes import ThemedTk
except:
    print('You must install the ttkthemes package to use GUI functionality. Please use pip install ttkthemes and then run python3 -m pip install git+https://github.com/RedFantom/ttkthemes \n')

import sys
print('Python version : ')
print(sys.version_info,'\n')
if(sys.version_info <(3, 0)):
    print('Please upgrade to python 3. \n')


print('If no prior prompt messages have appeared then your configuration should be sufficient. \n')
