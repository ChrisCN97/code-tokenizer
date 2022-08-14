from util import get_dataset
from server import S1, S2, S3
import os

langs = ["Java", "Python", "JavaScript", "PHP", "Ruby", "Go", "C#", "C++", "C", "Haskell", "Kotlin", "Fortran"]
train_config = {
    32: [100,100],
    "test": [2, 4],
    100: [100,100],
    300: [35,100],
    500: [20,100],
    700: [20,100],
    1000: [20,100],
    2000: [20,100],
    3000: [20,100],
    5000: [20,200],
    7000: [20,200],
    10000: [20,200]
}
def finetune(
        model_type="roberta",
        config_name="microsoft/codebert-base",
        model_name_or_path="microsoft/codebert-base",
        tokenizer_name="roberta-base",
        task_name="clone_detection",
        lang="Java",
        size=32,
        output="Java_32",
        do_train=True,
        freeze_plm=False,
        train_batch=10,
        epoch=20,
        eval_step=100,
        learning_rate=1e-5,
        do_test=True,
        env=S2,
        is_part=False,
        nohup=False,
        target_output_dir="Java_32",
        do_target_train=False
):
    cmd = "python ../method/finetune/code/run.py " \
          "--block_size 512 " \
          "--eval_batch_size 32 " \
          "--max_grad_norm 1.0 " \
          "--evaluate_during_training " \
          "--train_data_rate 1 " \
          "--seed 123456 "
    cmd += "--model_type {} ".format(model_type)
    cmd += "--config_name {} ".format(config_name)
    cmd += "--model_name_or_path {} ".format(model_name_or_path)
    cmd += "--tokenizer_name {} ".format(tokenizer_name)
    data_dir = "../method/finetune/dataset/{}/{}/{}".format(task_name, lang, size)
    if not os.path.exists(data_dir):
        if env != S2:
            print("Get dataset {}/{}/{} from server2".format(task_name, lang, size))
            get_dataset(method="finetune", task=task_name, lang=lang, size=size, from_server=S2)
        else:
            print("Dataset {}/{}/{} needs to be generated!".format(task_name, lang, size))
    cmd += "--data_folder {} ".format(data_dir)
    log_path = "output/{}/finetune/log/{}".format(task_name, output)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log = "{}/{}.log".format(log_path, lang)
    output = "output/{}/finetune/{}".format(task_name, output)
    if (do_test or do_target_train) and \
            (not os.path.exists(output) or not os.listdir(output)):
        print("Lack of {} for zero shot".format(output))
    cmd += "--output_dir {} ".format(output)
    if target_output_dir is not None:
        target_output = "output/{}/finetune/{}".format(task_name, target_output_dir)
        cmd += "--target_output_dir {} ".format(target_output)
    if freeze_plm:
        cmd += "--freeze_plm "
    cmd += "--train_batch_size {} ".format(train_batch)
    cmd += "--epoch {} ".format(epoch)
    cmd += "--learning_rate {} ".format(learning_rate)
    if do_train:
        cmd += "--do_train "
        cmd += "--save_steps {} ".format(eval_step)
    if do_target_train:
        cmd += "--do_target_train "
        cmd += "--save_steps {} ".format(eval_step)
    if do_test:
        cmd += "--do_eval "
        cmd += "--do_test "
        cmd += "--predictions_name pre_{}.txt".format(lang)
        cmd += "\npython ../method/finetune/evaluator/evaluator.py "
        cmd += "-a {}/test.txt ".format(data_dir)
        cmd += "-p {}/pre_{}.txt ".format(output, lang)
        cmd += "-o {}".format(log)
    if do_train or do_target_train:
        print(output)
    if is_part:
        return cmd
    if nohup:
        cmd = "nohup {} > output/{}/finetune/log/single.log 2>&1 &".format(cmd, task_name)
    else:
        cmd = "{} 2>&1 | tee output/{}/finetune/log/single.log".format(cmd, task_name)
    print(cmd)
    with open("run.sh", 'w') as f:
        f.write(cmd)

def gen_list(task_dicts, env, check_data=False):
    cmd = ""
    pre_time = 0
    for task in task_dicts:
        if task["size"] != "test":
            size_num = int(task["size"].split("_")[0])
        else:
            size_num = "test"
        if "epoch" not in task:
            task["epoch"] = train_config[size_num][0]
        if "eval_step" not in task:
            task["eval_step"] = train_config[size_num][1]
        if "target_output_dir" not in task:
            task["target_output_dir"] = None
            task["do_target_train"] = False
        c = finetune(
            config_name=task["model"],
            model_name_or_path=task["model"],
            task_name=task["task_name"],
            lang=task["lang"],
            size=task["size"],
            output=task["output"],
            epoch=task["epoch"],
            eval_step=task["eval_step"],
            do_train=task["do_train"],
            do_test=task["do_test"],
            env=env,
            is_part=True,
            target_output_dir=task["target_output_dir"],
            do_target_train=task["do_target_train"]
        )
        cmd += c + "\n"
        if task["do_train"] or task["do_target_train"]:
            if task["size"] == "test":
                pre_time += 0
            else:
                pre_time += int(task["epoch"])*size_num/10*0.011
        else:
            pre_time += 0.633
    print(cmd)
    if not check_data:
        with open("run.sh", 'w') as f:
            f.write(cmd)
    if env == S1:
        print("conda activate ptuning")
    if env == S3:
        print("/mnt/sda/cn/zeroshot/run\nconda activate pretrain_cuinan")
    print("nohup ./run.sh > output/{}/finetune/log/task_list.log 2>&1 &".format(task_dicts[0]["task_name"]))
    h, m = divmod(pre_time, 60)
    print("%dh %02dmin" % (h, m))

def get_local_model_name(task, name):
    return os.path.join("output", task, "finetue", name)

if __name__ == "__main__":
    # need test source domain
    task_dicts = []
    model_list = [
        ("microsoft/codebert-base", ""),
        # ("/mnt/sda/cn/zeroshot/method/pretrain/model/roberta_java", ""),
        # ("/mnt/sda/cn/zeroshot/method/pretrain/model/roberta_java_woSymbol", "_wosym"),
        # ("/mnt/sda/cn/zeroshot/method/pretrain/model/roberta_java_custom", "_custom"),
        # ("/mnt/sda/cn/zeroshot/method/pretrain/model/roberta_java_custom_fz", "_custom")
    ]
    task_list = [
        # ("clone_detection", 500, "BCB"),
        # ("clone_detection", 500, "Java"),
        # ("clone_detection", 1000, "BCB"),
        # ("clone_detection", 1000, "Java"),
        ("code_search", 500, "CSN"),
        ("code_search", 500, "Java"),
        # ("name_predict", 500, "Java"),
    ]
    for model, suffix in model_list:
        for task, size, lang in task_list:
            task_dicts.append({"task_name": task, "lang": lang, "size": "{}{}".format(size, suffix), "model": model,
                               "output": "{}_{}{}".format(lang, size, suffix), "do_train": True, "do_test": False})
            task_dicts.append({"task_name": task, "lang": lang, "size": "{}{}".format(size, suffix), "model": model,
                               "output": "{}_{}{}".format(lang, size, suffix), "do_train": False, "do_test": True})
    gen_list(task_dicts, S3, check_data=False)
    # s3 3060292 output/code_search/finetune/log/task_list.log 11:10

