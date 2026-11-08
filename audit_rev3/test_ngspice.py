import ctypes
import os

kicad_bin = r"C:\Program Files\KiCad\10.0\bin"
os.add_dll_directory(kicad_bin)
os.environ["PATH"] = kicad_bin + os.pathsep + os.environ.get("PATH", "")

ngspice = ctypes.CDLL(os.path.join(kicad_bin, "ngspice.dll"))

SENDCHAR = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
SENDSTAT = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
CONTROLLEDEXIT = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)

out_lines = []

@SENDCHAR
def cb_char(msg, ident, userdata):
    if msg:
        out_lines.append(msg.decode("utf-8", errors="replace"))
    return 0

@SENDSTAT
def cb_stat(msg, ident, userdata):
    return 0

@CONTROLLEDEXIT
def cb_exit(status, immediate, quitexit, ident, userdata):
    return 0

ngspice.ngSpice_Init(cb_char, cb_stat, cb_exit, None, None, None, None)
ngspice.ngSpice_Command(b"version -f")
print("".join(line + "\n" for line in out_lines[:15]))

