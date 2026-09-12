import os
import socket
import subprocess
import sys
import tempfile
import time

BASE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(tempfile.gettempdir(), "jsamadhan_start.lock")
PY = os.path.join(BASE, "venv", "Scripts", "python.exe")


def port_open():
    s = socket.socket()
    try:
        s.settimeout(0.4)
        s.connect(("127.0.0.1", 5000))
        s.close()
        return True
    except OSError:
        return False


try:
    fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
except OSError:
    sys.exit("another starter is running / lock exists")
os.write(fd, str(os.getpid()).encode())
os.close(fd)

try:
    if port_open():
        sys.exit("server already running on :5000")
    flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(
        [PY, "app.py"], cwd=BASE,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL, creationflags=flags,
    )
    for _ in range(15):
        time.sleep(0.5)
        if port_open():
            print("started - listening on :5000")
            sys.exit(0)
    sys.exit("started but :5000 did not open in time")
finally:
    try:
        os.unlink(LOCK)
    except OSError:
        pass
