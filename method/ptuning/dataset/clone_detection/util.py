import os
import json
import random
import shutil

SOURCE_PATH = "../../../../dataset/clone_detection"
TRAIN_PREFIX = "train_"
DEV = "dev_400.txt"
TEST = "test_1000.txt"

def get_url2code(lang, name='data.jsonl'):
    url_to_code = {}
    with open(os.path.join(SOURCE_PATH, lang, name)) as f:
        for line in f:
            line = line.strip()
            js = json.loads(line)
            url_to_code[js['idx']] = js['func']
    return url_to_code

def get_clear_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)
    return folder

def change_format(source, target, url_to_code, idx):
    jsonl_list = []
    with open(source) as f:
        for line in f:
            line = line.split()
            code1 = url_to_code[line[0]]
            code2 = url_to_code[line[1]]
            label = True if line[2] == "1" else False
            jsonl_list.append({
                "code1": code1,
                "code2": code2,
                "idx": idx,
                "label": label,
            })
            idx += 1
    with open(target, 'w') as f:
        random.shuffle(jsonl_list)
        for item in jsonl_list:
            f.write(json.dumps(item) + "\n")
    return idx

def gen_dataset(lang, size):
    if not os.path.exists(lang):
        os.mkdir(lang)
    folder = get_clear_folder(os.path.join(lang, size))
    url_to_code = get_url2code(lang)
    idx = 0
    idx = change_format(os.path.join(SOURCE_PATH, lang, "{}{}.txt".format(TRAIN_PREFIX, size)),
                        os.path.join(folder, "train.jsonl"), url_to_code, idx)
    idx = change_format(os.path.join(SOURCE_PATH, lang, DEV),
                        os.path.join(folder, "dev32.jsonl"), url_to_code, idx)
    change_format(os.path.join(SOURCE_PATH, lang, TEST),
                  os.path.join(folder, "val.jsonl"), url_to_code, idx)

if __name__ == "__main__":
    gen_dataset(lang="Java", size="32")