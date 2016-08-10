import sublime, sublime_plugin
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
            Momento.cache.update({ momento_item.project_name : momento_item })
        except Exception as e:
            print("Could not update cache due to: " + e)
        finally:
            lock.release()

    def get_item(project_name):
        lock = threading.RLock()
        lock.acquire()
        emptyItem = MomentoItem(project_name, [], "")
        try:
            return Momento.cache.get(project_name) or emptyItem
        except Exception as e:
            print("Could not update cache due to: " + e)
            return emptyItem
        finally:
            lock.release()

    def clear_items():
        lock = threading.RLock()
        lock.acquire()
        try:
            Momento.cache.clear()
        except Exception as e:
            print("Could not clear cache due to: " + e)
        finally:
            lock.release()

    def get_items():
        return Momento.cache.copy()

class MomentoItem:
    def __init__(self, project_name, classes_from_jars, jar_files_path):
        self.project_name        = project_name
        self.classes_from_jars   = classes_from_jars
        self.jar_files_path_hash = md5(jar_files_path)

    def should_refresh(self, current_jar_files_path):
        return (not self.classes_from_jars) or \
                self.jar_files_path_hash != md5(current_jar_files_path)

    def __str__(self):
        return self.project_name + " : " + str(len(self.classes_from_jars))

    __repr__ = __str__

class ScuggestClearCacheCommand(sublime_plugin.TextCommand):

    def is_enabled(self):
        return is_expected_env(self.view, sublime.version())

    def is_visible(self):
        return is_expected_env(self.view, sublime.version())

    def run(self, edit):
        print("clearing cache")
        Momento.clear_items()

class ScuggestShowCacheCommand(sublime_plugin.TextCommand):

    def is_enabled(self):
        return is_expected_env(self.view, sublime.version())

    def is_visible(self):
        return is_expected_env(self.view, sublime.version())

    def run(self, edit):
        items = Momento.get_items()
        if (len(items)):
            print("\nScuggest cache:")
            for k in items.keys():
                mi = items.get(k)
                print("\n" + str(mi))
        else:
            print("\nScuggest cache is empty.")
