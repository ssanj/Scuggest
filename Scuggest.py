import sublime, sublime_plugin
import re
from .matchers import *
from .tools import *
from .momento import *

class ScuggestAddImportCommand(sublime_plugin.TextCommand):

    def is_enabled(self):
        return hasattr(self, "view") and is_expected_env(self.view, sublime.version())

    def is_visible(self):
        return hasattr(self, "view") and is_expected_env(self.view, sublime.version())

    def update_cache(self, classes_from_jars, jar_files_path):
        #remove the filtered classes as they are not used in the search
        mi = MomentoItem(self.project_name, classes_from_jars, jar_files_path)
        Momento.set_item(mi)
        self.cache_item = Momento.get_item(self.project_name)

    def run(self, edit):
        print("-- ScuggestAddImportCommand -- ")
        project_name = get_project_name(self.view)
        if (project_name):
            self.project_name = project_name
            self.cache_item   = Momento.get_item(self.project_name)
        else:
            sublime.error_message(
                "Could not read .sublime-project file." +
                "\nCreate a project and add your Scuggest settings there." +
                "\nPlease see https://github.com/ssanj/Scuggest for more information.")
            return

        settings = self.view.settings()
        if not settings.has("scuggest_import_path"):
            settings = sublime.load_settings("Scuggest.sublime-settings")
            if not settings.has("scuggest_import_path"):
                sublime.error_message("You must first define \"scuggest_import_path\" in your settings")
                return

        if len(settings.get("scuggest_import_path")) == 0:
            sublime.error_message("You must first define at least one \"scuggest_import_path\" in your settings")
            return

        class_file_paths = settings.get("scuggest_import_path")
        filtered_path    = settings.get("scuggest_filtered_path") or []

        t = ScuggestAddImportThread(self, class_file_paths, filtered_path)
        t.start()
        self.handle_thread(t)

    def handle_thread(self, thread, dots = 0):
        if (thread.is_alive()):
             dots = (dots + 1) % 5
             self.view.set_status("scuggest", "Loading imports " + ("." * dots))
             sublime.set_timeout(lambda: self.handle_thread(thread, dots), 500)
             return
        else:
             self.view.erase_status("scuggest")
             sublime.status_message("Scuggest: loaded imports")

    def remove_filtered_classes(self, classes_list, filtered_path):
        return [cl for cl in classes_list if cl.find("$$anonfun$") == -1 and \
               cl.find("$$anon$") == -1 and \
               not re.match("^.*\$\d+\.class$", cl) and \
               not has_element(filtered_path, cl.startswith) and \
               cl.find("$delayedInit$body") == -1]

    def process_classes(self, classesList, filtered_path):
        allEmpty = True
        for sel in self.view.sel():
            if sel.empty():
                wordSel     = self.view.word(sel)
                wordContent = self.view.substr(wordSel)
                if not wordSel.empty() and re.findall("^[a-zA-Z][a-zA-Z0-9]+$", wordContent):
                    self.view.sel().add(wordSel)
                    sel = wordSel
                else:
                    continue

            userSelection = self.view.substr(sel)
            self.process_classes_in_ui(classesList, filtered_path)(userSelection)

            allEmpty = False

        if allEmpty:
            self.view.window().show_input_panel("Class name: ", "", self.process_classes_in_ui(classesList, filtered_path), None, None)

    def match_selection(self, classesList, filtered_path, userSelection):
        results = []
        matches = [EndsWithClassNameMatcher(), \
                   EndsWithObjectMatcher(),    \
                   ContainsMatcher(),          \
                   PrefixMatcher(),            \
                   SuffixMatcher(),            \
                   ObjectSubtypesMatcher()]

        print("classesList: " + str(len(classesList)))
        count = 0
        for name in classesList:
            count = count + 1
            for m in matches:
                if (m.does_match(name, userSelection)):
                    m.add_result(name, userSelection, results)
                    break

        print("classes scanned: " + str(count))
        return sorted(list(set(results)))

    def process_classes_in_ui(self, classesList, filtered_path):
        def with_user_selection(userSelection):
            results = timed("match_selection")(self.match_selection(classesList, filtered_path, userSelection))
            if len(results) == 1:
                self.select_class(results)(0)
            elif len(results) > 1:
                self.view.window().show_quick_panel(results, self.select_class(results))
            else:
                sublime.error_message("There is no such class in \"scuggest_import_path\"")

        return with_user_selection

    def select_class(self, results):
        def with_index(index):
            if index == -1:
                return
            self.view.run_command("scuggest_add_import_insert", {"classpath": results[index]})

        return with_index

class ScuggestAddImportInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, classpath):
        for i in range(0,10000):
            point = self.view.text_point(i,0)
            region = self.view.line(point)
            line = self.view.substr(region)

            # if not a single comment, block comment, package or package object or an empty line
            # then insert import at the next line which should be some valid construct.
            if not re.match("^[\s\t]*\/\*\*?[\s\t]*.*$", line) and \
               not re.match("^[\s\t]*\/\/.*$",  line) and \
               not re.match("^[\s\t]*package[\s\t]+(?:object)?(?:[\s\t]+)?[a-zA-Z][a-zA-Z0-9]+(?:\.(?:[a-zA-Z][a-zA-Z0-9]+))*$", line) and \
               not re.match("^[\s\t]*$", line):
                   importStatement = "import " + classpath
                   #if the previous line is also an import then just add above
                   #if not then add an extra line to separate the import block
                   if re.match("^[\s\t]*import[\s\t]+.*$", line):
                     importStatementNL = importStatement + "\n"
                   else:
                     importStatementNL = importStatement + "\n\n"
                   self.view.insert(edit, point, importStatementNL)
                   break

class ScuggestAddImportThread(threading.Thread):
    def __init__(self, command, class_file_paths, filtered_path):
        self.command          = command
        self.class_file_paths = class_file_paths
        self.filtered_path    = filtered_path
        threading.Thread.__init__(self)

    def run(self):
        (jar_files_path, dir_files_path) = partition_file_paths(self.class_file_paths)

        if self.command.cache_item.should_refresh(jar_files_path):
            self.command.update_cache(timed("load_classes_from_jars")(
                self.command.remove_filtered_classes(
                    load_classes(jar_files_path), self.filtered_path)),
                    jar_files_path)

        classes_from_dirs = timed("load_classes_from_dirs")(
                                self.command.remove_filtered_classes(
                                    load_classes(dir_files_path), self.filtered_path))

        self.command.process_classes(self.command.cache_item.classes_from_jars + classes_from_dirs, self.filtered_path)
