"""
程序运行器
"""
import subprocess
from os.path import basename as filename
from os.path import dirname, abspath
from os import getcwd,chdir
import time
import platform

def run(file, stdin=None, timeout=1):
    if platform.system() == "Linux":
        system("chmod +x " + repr(file))
    if stdin is not None:
        stdin = open(stdin, "r")
    else:
        stdin = ""
    if isinstance(file, str):
        file = [file]
    try:
        begin = time.time()
        process = subprocess.run(file,stdin=stdin,timeout=timeout,capture_output=True,encoding="utf-8")
        end=time.time()
    except subprocess.TimeoutExpired:
        raise TimeoutError("%s 超出时间限制" % filename(file[0]))
    if process.returncode != 0:
        raise RuntimeError("%s 返回非零值 %d" % (filename(file[0]), process.returncode))
    return [process.stdout,process.stderr,end-begin]

