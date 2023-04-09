import sys
import os
import subprocess
from tkinter import messagebox

PATH = os.path.abspath(os.path.dirname(__file__))


def check_firstStart():
    with open(os.path.join(PATH,'is_first_start.txt'),'r') as f:
        if str(f.readlines()[0]) == 'FIRST_START':
            # Install all dependencies using pip
            subprocess.check_call(f'pip install -r "{os.path.join(PATH,"requirements.txt")}"')
            # Check if playwright is installed
            try:
                import playwright
            except ImportError:
                # Install playwright if it is not installed
                subprocess.check_call(['playwright', 'install'])
            with open(os.path.join(PATH,'is_first_start.txt'),'w') as w:
                w.write('Installed')
                messagebox.showinfo("Finished","Dependencies Installed, you can start the app now!")
                sys.exit()
        else:
            pass

if __name__ == '__main__':
    print(PATH)
    check_firstStart()
