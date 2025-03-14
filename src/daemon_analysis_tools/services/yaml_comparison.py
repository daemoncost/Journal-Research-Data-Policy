import yaml
from deepdiff import DeepDiff

def compare_yaml_files(path1: str, path2: str) -> None:
    """
    Compare two YAML files and print the differences.

    This function loads two YAML files, compares them using DeepDiff,
    and prints any differences found. It ignores ordering differences.

    :param path1: Path to the first YAML file.
    :param path2: Path to the second YAML file.
    """
    with open(path1, "r") as f1:
        yaml1 = yaml.safe_load(f1)
    with open(path2, "r") as f2:
        yaml2 = yaml.safe_load(f2)

    diff = DeepDiff(yaml1, yaml2, ignore_order=True)
    if diff:
        print("Differences found:")
        print(diff)
    else:
        print("No differences found.")
