import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": []}

# GUI applications require a different base on Windows (the default is for
# a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "PySong",
        version = "0.1",
        description = "MP3 library manager",
        options = {"build_exe": build_exe_options},
        executables = [Executable('D:\\Python\\final\\source\\main.py', base=base)])