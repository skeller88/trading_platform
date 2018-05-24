import os
import sys


def append_dir_paths(dirs):
    (root, current_dir) = os.path.split(os.getcwd())
    for dir in dirs:
        sys.path.append(os.path.join(root, dir))
