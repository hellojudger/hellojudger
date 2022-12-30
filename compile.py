import json, os, shutil, subprocess
import uuid


def compile_cpp(source, version, optimization):
    fn = str(uuid.uuid4())
    compiler_settings = json.load(open("settings/compiler.json", "r", encoding="utf-8"))
    version_command = ""
    for i in compiler_settings["versions"]:
        if i["name"] == version:
            version_command = i["argument"]
    optimization_command = ""
    for i in compiler_settings["optimizations"]:
        if i["name"] == optimization:
            version_command = i["argument"]
    if not os.path.isdir("compiling"):
        os.mkdir("compiling")
    with open("compiling/%s.cpp" % fn, "w", encoding="utf-8") as f:
        f.write(source)
    command = compiler_settings["compiler"] + " \"compiling/%s.cpp\" -o \"compiling/%s.exe\" " % (fn, fn) + " ".join(
        compiler_settings["arguments"]) + " " + version_command + optimization_command
    (status, output) = subprocess.getstatusoutput(command)
    if status != 0:
        raise Exception("编译错误")
    return "compiling/%s.exe" % fn
