import os.path
import gzip
import json
from tqdm import tqdm
import rules

# on S3
ROOT_PATH = "/mnt/sda/codeSearchNet"
MAX_LENGTH = 514


def get_source_files(lang, data_type):
    source_path = os.path.join(ROOT_PATH, lang, "final", "jsonl", data_type)
    return source_path, os.listdir(source_path)


def make_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def json_gz_parse(path):
    g = gzip.open(path, 'rb')
    for l in g:
        yield json.loads(l)


def preprocess(lang, dataset_folder_name, data_type, rules=[]):
    source_path, files = get_source_files(lang, data_type)
    make_folder(dataset_folder_name)
    dataset_file_name = data_type + ".txt"
    dataset_file = open(os.path.join(dataset_folder_name, dataset_file_name), 'w')
    for file in tqdm(files):
        for data in json_gz_parse(os.path.join(source_path, file)):
            length = len(data["code_tokens"]) + len(data["docstring_tokens"])
            if length > MAX_LENGTH:
                continue
            doc = data["docstring"]
            code = data["code"]
            text = doc + " " + code
            for rule in rules:
                text = rule(text)
            if len(text) > 0:
                dataset_file.write(text + "\n")
    dataset_file.close()


if __name__ == "__main__":
    DATA_TYPES = ["train", "valid", "test"]
    preprocess(lang="java", dataset_folder_name="java_custom", data_type=DATA_TYPES[1],
               rules=[rules.java])

