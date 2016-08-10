import zipfile
import os
from time import perf_counter as pc
import hashlib

def get_classes_list(path):
    if path.endswith(".jar"):
        zipF = zipfile.ZipFile(path, "r")
        classes_list = zipF.namelist()
        zipF.close()
        return classes_list
    else:
        classes_list = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                classes_list.insert(0, (root + "/" + filename)[len(path):])

        return classes_list

def load_classes(class_paths):
    all_classes = []
    for path in class_paths:
        all_classes.insert(0, get_classes_list(path))

    return [clzz.replace("\\", "/") for class_list in all_classes for clzz in class_list]

def partition_file_paths(file_paths):
    from_dirs = []
    from_jars = []

    for path in file_paths:
        if path.endswith(".jar"):
            from_jars.append(path)
        else:
            from_dirs.append(path)

    return (from_jars, from_dirs)

def has_element(elements, f):
    for e in elements:
        if f(e):
            return True
    return False

def timed(name):
    start  = pc()
    def with_function(result):
        end = pc()
        print(name + ": " + str(end - start) + "s")
        return result
    return with_function

def md5(content):
    return hashlib.md5(str(content).encode("utf-8")).hexdigest()

def get_project_name(view):
    if view and view.window():
        return view.window().project_file_name()
    else:
        return ""

def is_expected_env(view, version):
    if get_project_name(view) and \
       view and \
       view.settings() and \
       view.settings().has("syntax"):
        syntax = view.settings().get('syntax')
        if (int(version) <= 3083):
            return syntax.endswith("Scala.tmLanguage")
        else:
            return syntax.endswith("Scala.sublime-syntax")
    else:
        return False