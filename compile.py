import json, os, shutil, subprocess
import uuid, platform


def compile_cpp(source, version, optimization, extra_file = None):

    if extra_file is not None:
        with open(extra_file, "r", encoding="utf-8") as f:
            testlib = f.read()
        source = testlib + "\n\n" + source
    fn = str(uuid.uuid4())
    compiler_settings = json.load(open("settings/compiler.json", "r", encoding="utf-8"))
    version_command = ""
    for i in compiler_settings["versions"]:
        if i["name"] == version:
            version_command = i["argument"]
    optimization_command = ""
    for i in compiler_settings["optimizations"]:
        if i["name"] == optimization:
            optimization_command = i["argument"]
    if not os.path.isdir("compiling"):
        os.mkdir("compiling")
    with open("compiling/%s.cpp" % fn, "w", encoding="utf-8") as f:
        f.write(source)
    headers = []
    headers.append("compiling/%s.cpp" % fn)
    headers = list(map(lambda x:"\"%s\""%x, headers))
    command = compiler_settings["compiler"] + " " + ' '.join(headers) + " -o \"compiling/%s.exe\" " % (fn) + " ".join(
        compiler_settings["arguments"]) + " " + version_command + " " + optimization_command
    if platform.system() == "Windows":
        command += " -mwindows"
    (status, output) = subprocess.getstatusoutput(command)
    if status != 0:
        raise Exception("编译错误")
    return "compiling/%s.exe" % fn
