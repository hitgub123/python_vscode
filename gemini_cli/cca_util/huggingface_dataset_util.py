from datasets import load_dataset, load_from_disk
from datasets import Dataset

dataset_path = "./dataset/"


def get_dataset(name):
    save_path = dataset_path + name
    try:
        test_dataset = load_from_disk(save_path)
    except:
        test_dataset = load_dataset(name)
        test_dataset.save_to_disk(save_path)
    return test_dataset


if __name__ == "__main__":
    name="JC-24/meta-record-ragas-synthetic-dataset"
    get_dataset(name)
