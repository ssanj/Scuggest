import threading
from .tools import *

class Momento:
    cache = {}
    classes_list = []
    path_hash = None

    def set_item(momento_item):
        lock = threading.RLock()
        lock.acquire()
        try:
            Momento.cache.update(momento_item.toMap())
        except Exception as e:
            print("Could not update cache due to: " + e)
        finally:
            lock.release()

    def get_item(project_name):
        lock = threading.RLock()
        lock.acquire()
        try:
            result = Momento.cache.get(project_name)
            if result:
                return result
            else:
                return MomentoItem(project_name, [], "")
        except Exception as e:
            print("Could not update cache due to: " + e)
            return MomentoItem(project_name, [], "")
        finally:
            lock.release()

class MomentoItem:
    def __init__(self, project_name, classes_from_jars, jar_files_path):
        self.project_name        = project_name
        self.classes_from_jars   = classes_from_jars
        self.jar_files_path_hash = md5(jar_files_path)

    def toMap(self):
        return {
                 self.project_name: {
                    "classes_from_jars"   : self.classes_from_jars,
                    "jar_files_path_hash" : self.jar_files_path_hash
                 }
               }

    def should_refresh(self, current_jar_files_path):
        return (not self.classes_from_jars) or \
                self.jar_files_path_hash != md5(current_jar_files_path)


