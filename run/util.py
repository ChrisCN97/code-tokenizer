import os
import shutil
from server import S1, S2, USER, IP
import matplotlib.pyplot as plt
import numpy as np
import re

langs = ["Java", "Python", "JavaScript", "PHP", "Ruby", "Go", "C#", "C++", "C", "Haskell", "Kotlin", "Fortran"]

def get_clear_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)
    return folder

def scp_get(source, target, port, user=USER, ip=IP):
    os.system("scp -r -P {} {}@{}:{} {}".format(port, user, ip, source, target))

def get_dataset(method, task, lang, size, from_server):
    source = os.path.join(from_server["root"], "method", method, "dataset", task, lang, str(size))
    target = os.path.join("../method", method, "dataset", task, lang)
    if not os.path.exists(target):
        os.makedirs(target)
    target = os.path.join(target, str(size))
    scp_get(source, target, from_server["port"])

def get_output(method, task, name, from_server):
    source = os.path.join(from_server["root"], "run/output", task, method, name)
    target = os.path.join("output", task, method)
    scp_get(source, target, from_server["port"])

def plot_loss(folder, name):
    # name: acc.npy / loss.npy
    loss_list = np.load(os.path.join(folder, name))
    print(len(loss_list))
    plt.figure()
    plt.plot(np.arange(len(loss_list)), loss_list)
    plt.title("{}: {}".format(folder, name))
    plt.show()

def ptuning_log_reader(f):
    res_line = f.readlines()[-6]
    return re.search(r"\d.\d*", res_line).group()

def finetune_log_reader(f):
    res_line = f.read()
    return re.search(r"'acc': (\d+.\d+)", res_line).group(1)

def log_checker(task, method, output_name):
    log_folder = os.path.join("output", task, method, "log", output_name)
    logs = os.listdir(log_folder)
    log_dict = dict()
    for log in logs:
        lang = log.split(".")[0]
        with open(os.path.join(log_folder, log)) as f:
            if method == "ptuning":
                res = ptuning_log_reader(f)
            if method == "finetune":
                res = finetune_log_reader(f)
        log_dict[lang] = res
    return log_dict

def log_format(task, method, output_name, langs):
    log_dict = log_checker(task, method, output_name)
    for l in langs:
        print(log_dict[l])
    # if method == "ptuning":
    #     ptuning_time_reader(task, output_name)

def ptuning_time_reader(task, output_name):
    lang = output_name.split("_")[0]
    log = os.path.join("output", task, "ptuning/log", output_name, lang+".log")
    with open(log) as f:
        print(re.search(r"\d+:\d+:\d+", f.readlines()[-2]).group())

if __name__ == "__main__":
    # get_output(method="finetune", task="clone_detection", name="BCB_32_b", from_server=S2)
    # get_dataset(method="ptuning", task="clone_detection", lang="Java", size="7000", from_server=S2)
    # plot_loss(folder="output/clone_detection/ptuning/BCB_32_b/p10-i0", name="acc.npy")
    # plot_loss(folder="output/clone_detection/finetune/BCB_32_b", name="acc.npy")
    log_format("clone_detection", "ptuning", "BCB_32_b", langs=["BCB","Python", "JavaScript", "PHP", "Ruby", "Go", "C#", "C++", "C", "Haskell", "Kotlin", "Fortran"])
    # for size in [3000,1000,500,100]:
    #     log_format("code_search", "ptuning", "Devign_{}".format(size), langs=["Devign"])