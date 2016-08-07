import zipfile
import os
from time import perf_counter as pc

def get_classes_list(path):
    if path.endswith(".zip") or path.endswith(".jar"):
        zipF = zipfile.ZipFile(path, "r")
        classesList = zipF.namelist()
        zipF.close()
        return classesList
    else:
        classesList = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                classesList.append((root + "/" + filename)[len(path):])
        return classesList

def has_element(elements, f):
    for e in elements:
        if f(e):
            return True
    return False


def timeit(name, fun):
    start = pc()
    f()
    end = pc()
    print(name + ": " + str(end - start) + "s")