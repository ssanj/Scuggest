import threading
from .tools import *

class Momento:
    classes_list = []
    path_hash = None

    def set_classes_list(class_paths, classes_list):
        lock = threading.RLock()
        lock.acquire()
        try:
            Momento.classes_list = classes_list
            Momento.path_hash    = md5(class_paths)
        except Exception as e:
            print("Could not update classes_list due to: " + e)
        finally:
            lock.release()