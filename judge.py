"""
答案校验器
"""
import ast
import math
import run
from bs4 import BeautifulSoup
import os
import compile
import platform
import json


def line_compare(input, output, answer):
    with open(input, "r", encoding="utf-8") as f:
        input = f.read()
    with open(output, "r", encoding="utf-8") as f:
        output = f.read()
    with open(answer, "r", encoding="utf-8") as f:
        answer = f.read()
    output = output.splitlines()
    answer = answer.splitlines()
    if len(output) != len(answer):
        return ["Presentation Error", "读到 %d 行,但期望 %d 行" % (len(output), len(answer)), 0]
    for i in range(len(output)):
        if output[i] != answer[i]:
            return ["Wrong Answer", "在第 %d 行,读到 %s,但期望 %s" % (i + 1, output[i], answer[i]), 0]
    return ["Accepted", "通过,共 %d 行" % len(output), 1]


def __get_tokens(content):
    content = str(content)
    contents = []
    buffer = ""
    for i in range(len(content)):
        if content[i].isspace():
            if buffer != "" and not buffer.isspace():
                contents.append(buffer)
            buffer = ""
        else:
            buffer += content[i]
    if buffer != "" and not buffer.isspace():
        contents.append(buffer)
    return contents


def token_compare(input, output, answer):
    with open(input, "r", encoding="utf-8") as f:
        input = f.read()
    with open(output, "r", encoding="utf-8") as f:
        output = f.read()
    with open(answer, "r", encoding="utf-8") as f:
        answer = f.read()
    oc = __get_tokens(output)
    ac = __get_tokens(answer)
    if len(oc) != len(ac):
        return ["Presentation Error", "读到 %d 个记号,期望 %d 个记号" % (len(oc), len(ac)), 0]
    for i in range(len(oc)):
        if oc[i] != ac[i]:
            return ["Wrong Answer", "在第 %d 个记号,读到 %s,期望 %s" % (i + 1, oc[i], ac[i]), 0]
    return ["Accepted", "通过,共 %d 个记号" % len(oc), 1]


def float_compare(input, output, answer, eps):
    with open(input, "r", encoding="utf-8") as f:
        input = f.read()
    with open(output, "r", encoding="utf-8") as f:
        output = f.read()
    with open(answer, "r", encoding="utf-8") as f:
        answer = f.read()
    oc = __get_tokens(output)
    ac = __get_tokens(answer)
    if len(oc) != len(ac):
        return ["Presentation Error", "读到 %d 个浮点数,期望 %d 个浮点数" % (len(oc), len(ac)), 0]
    for i in range(len(oc)):
        try:
            of = float(oc[i])
        except (ValueError, OverflowError):
            return ["Presentation Error", "在第 %d 个浮点数,读到 %s,这不是合法的浮点数" % (i + 1, oc[i]), 0]
        try:
            af = float(ac[i])
        except (ValueError, OverflowError):
            return ["Presentation Error", "在第 %d 个浮点数,期望 %s,这不是合法的浮点数" % (i + 1, ac[i]), 0]
        if math.fabs(of - af) > eps:
            return ["Wrong Answer", "在第 %d 个浮点数,读到 %s,期望 %s,误差 %.10f" % (i + 1, oc[i], ac[i], math.fabs(of - af)), 0]
    return ["Accepted", "通过,共 %d 个浮点数" % len(oc), 1]


def integer_compare(input, output, answer):
    with open(input, "r", encoding="utf-8") as f:
        input = f.read()
    with open(output, "r", encoding="utf-8") as f:
        output = f.read()
    with open(answer, "r", encoding="utf-8") as f:
        answer = f.read()
    oc = __get_tokens(output)
    ac = __get_tokens(answer)
    if len(oc) != len(ac):
        return ["Presentation Error", "读到 %d 个整数,期望 %d 个整数" % (len(oc), len(ac)), 0]
    for i in range(len(oc)):
        try:
            of = int(oc[i])
        except ValueError:
            return ["Presentation Error", "在第 %d 个整数,读到 %s,这不是合法的整数" % (i + 1, oc[i]), 0]
        try:
            af = int(ac[i])
        except ValueError:
            return ["Presentation Error", "在第 %d 个整数,期望 %s,这不是合法的整数" % (i + 1, ac[i]), 0]
        if of != af:
            return ["Wrong Answer", "在第 %d 个整数,读到 %s,期望 %s" % (i + 1, oc[i], ac[i]), 0]
    return ["Accepted", "通过,共 %d 个整数" % len(oc), 1]

compiled_ = {}

def testlib_checker_compare(input, output, answer, checker):
    print(checker)
    compiler_settings = json.load(open("settings/compiler.json", "r", encoding="utf-8"))
    def rep(s):
        return "\"" + os.path.abspath(s) + "\""  
    checker.replace("\\", "/")
    if checker not in compiled_.keys() or not os.path.isfile(compiled_[checker]):
        pck = checker
        with open(checker, "r", encoding="utf-8") as f:
            checker = f.read()
        checker = compile.compile_cpp(checker, "C++ 14", "O2")
        compiled_[pck] = checker
    else:
        checker = compiled_[checker]
    if platform.system() == "Linux":
        system("chmod -R 777 compiling/")
    checker = rep(checker)
    input = rep(input)
    output = rep(output)
    answer = rep(answer)
    os.popen(' '.join([checker, input, output, answer, 'report.xml', '-appes'])).close()
    # run.run(' '.join([checker, input, output, answer,'report.xml','-appes']),timeout=2)
    xml = ""
    with open("report.xml", "r", encoding="windows-1251") as f:
        xml = f.read()
    soup = BeautifulSoup(xml, "xml").select_one("result")
    result = str(soup.attrs.get("outcome")).replace("-", " ").title()
    points = 0.0
    if result == "Points":
        result = "Partly Correct"
        points = float(soup.attrs.get("points"))
    if result == "Accepted":
        points = 1.0
    return [result, soup.text, points]


def closure(function, args=[]):  # 简易闭包
    def _calling(input, output, answer):
        return function(input, output, answer, *args)

    return _calling

