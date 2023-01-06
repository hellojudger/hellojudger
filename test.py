"""
测试题目
"""

import judge as j_
import run
import shutil
from os import mkdir, listdir, system
from os.path import abspath, join as path_join
from os.path import isdir
from os.path import dirname
import yaml
import uuid
import platform


class Task:
    input = ""
    answer = ""
    time = 0
    memory = 0

    def __init__(self, input, answer, time, memory=0):
        self.input = input
        self.answer = answer
        self.time = time
        self.memory = memory


def judge_one(program, task, judger):
    if not isdir("checking"):
        mkdir("checking")
    filename = "checking/" + str(uuid.uuid4()) + ".exe"
    if platform.system() == "Linux":
        system("chmod -R 777 checking/")
    try:
        shutil.copyfile(program, filename)
    except BaseException as e:
        return ["Internal Error", repr(e), 0, 0]
    program = filename
    try:
        result = run.run(program, task.input, task.time)
        cost_time = result[2]
        result = result[0]
    except TimeoutError as e:
        return ["Time Limit Exceed", str(e), 0, task.time]
    except RuntimeError as e:
        return ["Runtime Error", str(e), 0, 0]
    except BaseException as e:
        return ["Internal Error", repr(e), 0, 0]
    output_id = str(uuid.uuid4())
    with open(path_join(abspath("checking/"), "%s.out" % output_id), "w") as f:
        f.write(result)
    judged = judger(task.input, path_join(abspath("checking/"), "%s.out" % output_id), task.answer)
    judged.append(cost_time)
    return judged

def time_iden(content, default):
    if content is None:
        return default
    if content.endswith("ms"):
        return int(content[:-2]) / 1000
    if content.endswith("s"):
        return float(content[:-1])
    raise ValueError()


def _debug_juding_slot(type, data):
    if type == "subtask_begin":
        print("Subtask %d" % data["id"])
    if type == "task_finished":
        print("%s/%s\t%s\t%s\t%.4lfs\t%.2f Pts" % (
            data["input"], data["output"], data["sta"], data["msg"], data["time"], data["pts"]))
    if type == "subtask_ignored":
        print("被忽略")


def judge_problem(config_path: str, program, slot=_debug_juding_slot):
    all_accepted = True
    j_.compiled = {}
    total = 0
    datadir = dirname(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config = f.read()
    try:
        config = yaml.load(config, Loader=yaml.FullLoader)
    except BaseException as e:
        raise ValueError(repr(e))
    if config.get("type", "default") != "default":
        raise ValueError("不支持的题目类型 %s" % config["type"])
    try:
        default_time = time_iden(config.get("time"), 1)
    except ValueError:
        raise ValueError("错误的时间限制")
    checker = config.get("checker_type", "default")
    if checker == "default":
        judger = j_.closure(j_.token_compare)
    elif checker == "strict":
        judger = j_.closure(j_.line_compare)
    elif checker == "real":
        judger = j_.closure(j_.float_compare, [pow(10, -int(config.get("eps", 4)))])
    elif checker == "integer":
        judger = j_.closure(j_.integer_compare)
    elif checker == "testlib":
        judger = j_.closure(j_.testlib_checker_compare, [path_join(datadir, config.get("checker"))])
    else:
        raise ValueError("不支持的评测器")
    slot("judge_begin", {})
    if config.get("cases") is None and config.get("subtasks") is None:
        slot("scan_begin", {})
        files = listdir(datadir)
        cases = []
        for i in files:
            if i.endswith(".in") and i[:-3] + ".out" in files:
                slot("scan_find_task", {"input": i, "output": i[:-3] + ".out"})
                cases.append({"input": i, "output": i[:-3] + ".out"})
            elif i.endswith(".in") and i[:-3] + ".ans" in files:
                slot("scan_find_task", {"input": i, "output": i[:-3] + ".ans"})
                cases.append({"input": i, "output": i[:-3] + ".ans"})
        config["cases"] = cases
        slot("scan_finished", {"cases": cases})
    if config.get("cases") is not None:
        per = 100.0 / len(config["cases"])
        slot("cases_begin", {})
        for i in config["cases"]:
            input = i.get("input")
            output = i.get("output")
            time = time_iden(i.get("time"), default_time)
            if input is None or output is None:
                raise ValueError("缺少输入输出")
            slot("task_begin", {"input": input, "output": output})
            result = judge_one(program, Task(path_join(datadir, input), path_join(datadir, output), time), judger)
            if result[0] != "Accepted":
                all_accepted = False
            slot("task_finished",
                 {"input": input, "output": output, "sta": result[0], "msg": result[1], "pts": per * result[2],
                  "time": result[3]})
            total += per * result[2]
        slot("cases_finished", {})
    else:
        status = {}
        slot("subtasks_begin", {})
        now_subtask = -1
        for subtask in config["subtasks"]:
            now_subtask = subtask.get("id", now_subtask + 1)
            slot("subtask_begin", {"id": now_subtask})
            subtask_time = time_iden(subtask.get("time"), default_time)
            subtask_type = eval(subtask.get("type", "sum"))
            subtask_score = subtask["score"]
            per = 0
            if subtask.get("type", "sum") == "sum":
                per = subtask_score / len(subtask["cases"])
            else:
                per = subtask_score
            if_ = subtask.get("if", [])
            can_judge = True
            accepted = True
            alls = []
            for i in if_:
                if status[int(i)] != 1:
                    can_judge = False
                    break
            if not can_judge:
                slot("subtask_ignored", {"id": now_subtask})
                status[now_subtask] = 0
                continue
            for i in subtask["cases"]:
                input = i.get("input")
                output = i.get("output")
                time = time_iden(i.get("time"), subtask_time)
                if input is None or output is None:
                    raise ValueError("缺少输入输出")
                slot("task_begin", {"input": input, "output": output})
                result = judge_one(program, Task(path_join(datadir, input), path_join(datadir, output), time), judger)
                slot("task_finished",
                     {"input": input, "output": output, "sta": result[0], "msg": result[1], "pts": per * result[2],
                      "time": result[3]})
                alls.append(per * result[2])
                if result[2] != 1:
                    accepted = False
                if result[0] != "Accepted":
                    all_accepted = False
            status[now_subtask] = accepted
            slot("subtask_finished", {"id": now_subtask, "total": subtask_type(alls)})
            total += subtask_type(alls)
        slot("subtasks_finished", {})
    slot("judge_finished", {})
    return (all_accepted, total)
