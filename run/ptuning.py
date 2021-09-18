from util import get_dataset
from server import S1, S2
import os

def ptuning(
        model_type="roberta",
        model_name_or_path="microsoft/codebert-base",
        embed_size=768,
        task_name="clone_detection",
        lang="Java",
        size=32,
        output="Java_32",
        do_train=True,
        freeze_plm=False,
        pattern_ids=10,
        train_batch=5,
        max_step=100,
        eval_step=50,
        pet_repetitions=1,
        zeroshot=False,
        show_limit=0,
        env=S2,
        is_part=False,
        nohup=False
):
    cmd = "python3 ../method/ptuning/cli.py " \
          "--pet_per_gpu_eval_batch_size 16 " \
          "--pet_gradient_accumulation_steps 1 " \
          "--pet_max_seq_length 512 "
    cmd += "--model_type {} ".format(model_type)
    cmd += "--model_name_or_path {} ".format(model_name_or_path)
    cmd += "--embed_size {} ".format(embed_size)
    task_map = {"clone_detection": "clonedet"}
    cmd += "--task_name {} ".format(task_map[task_name])
    data_dir = "../method/ptuning/dataset/{}/{}/{}".format(task_name, lang, size)
    if not os.path.exists(data_dir):
        if env != S2:
            print("Get dataset {}/{}/{} from server2".format(task_name, lang, size))
            get_dataset(method="ptuning", task=task_name, lang=lang, size=size, from_server=S2)
        else:
            print("Dataset {}/{}/{} needs to be generated!".format(task_name, lang, size))
    cmd += "--data_dir {} ".format(data_dir)
    log_path = "output/{}/ptuning/log/{}".format(task_name, output)
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log = "{}/{}.log".format(log_path, lang)
    output = "output/{}/ptuning/{}".format(task_name, output)
    if zeroshot and \
            (not os.path.exists(output) or not os.listdir("{}/p{}-i0".format(output, pattern_ids))):
        print("Lack of {} for zero shot".format(output))
    cmd += "--output_dir {} ".format(output)
    if do_train:
        cmd += "--do_train "
        cmd += "--overwrite_output_dir "
    cmd += "--do_eval "
    if freeze_plm:
        cmd += "--freeze_plm "
    cmd += "--pattern_ids {} ".format(pattern_ids)
    cmd += "--pet_per_gpu_train_batch_size {} ".format(train_batch)
    cmd += "--pet_max_steps {} ".format(max_step)
    cmd += "--pet_repetitions {} ".format(pet_repetitions)
    cmd += "--show_limit {} ".format(show_limit)
    cmd += "--eval_every_step {} ".format(eval_step)
    if do_train:
        print("{}/p{}-i0".format(output, pattern_ids))
    if is_part:
        cmd = "{} 2>&1 | tee {}".format(cmd, log)
        return cmd
    if nohup:
        cmd = "nohup {} > {} 2>&1 &".format(cmd, log)
    else:
        cmd = "{} 2>&1 | tee {}".format(cmd, log)
    print(cmd)
    with open("run.sh", 'w') as f:
        f.write(cmd)

def ptuning_clone_detection_list(task_dicts, env):
    cmd = ""
    for task in task_dicts:
        c = ptuning(
            lang=task["lang"],
            size=task["size"],
            output=task["output"],
            do_train=task["do_train"],
            freeze_plm=task["freeze_plm"],
            max_step=task["max_step"],
            eval_step=task["eval_step"],
            zeroshot=task["zeroshot"],
            env=env,
            is_part=True)
        cmd += c + "\n"
    print(cmd)
    with open("run.sh", 'w') as f:
        f.write(cmd)
    if env == S1:
        print("conda activate ptuning")
    print("nohup ./run.sh > output/clone_detection/ptuning/log/task_list.log 2>&1 &".format(cmd))

def log_checker(output_name, lang, langs):
    log_folder = os.path.join("output/clone_detection/ptuning/log", output_name)


if __name__ == "__main__":
    # task_dicts = [{"lang": "Java", "size": 5000, "output": "Java_5000_2", "do_train": True, "freeze_plm": False,
    #      "max_step": 4000, "eval_step": 100, "zeroshot": False}]
    task_dicts = []
    langs = ["Python", "JavaScript", "PHP", "Ruby", "Go", "C#", "C++", "C", "Haskell", "Kotlin", "Fortran"]
    for size in [2500, 1000, 500, 32]:
        task_dicts.append(
            {"lang": "Java", "size": size, "output": "Java_{}".format(size), "do_train": True, "freeze_plm": False,
             "max_step": 2500, "eval_step": 80, "zeroshot": False})
        for lang in langs:
            task_dicts.append({"lang": lang, "size": 32, "output": "Java_{}".format(size), "do_train": False, "freeze_plm": False,
             "max_step": 10, "eval_step": 5, "zeroshot": True})
    ptuning_clone_detection_list(task_dicts, S2)