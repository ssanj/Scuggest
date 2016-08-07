import sublime, sublime_plugin
import re
from .matchers import *
from .tools import *

class ScuggestAddImportCommand(sublime_plugin.TextCommand):

    def load_classes(self, classPaths):
        clazzList = []
        for path in classPaths:
            clazzList = clazzList + get_classes_list(path)
            clazzList = list(map(lambda x: x.replace("\\", "/"), clazzList))

        self.classesList = clazzList

    def run(self, edit):
        debug = True
        settings = self.view.settings()
        if not settings.has("scuggest_import_path"):
            settings = sublime.load_settings("Scuggest.sublime-settings")
            if not settings.has("scuggest_import_path"):
                sublime.error_message("You must first define \"scuggest_import_path\" in your settings")
                return

        if len(settings.get("scuggest_import_path")) == 0:
            sublime.error_message("You must first define at least one \"scuggest_import_path\" in your settings")
            return

        self.filtered_path = settings.get("scuggest_filtered_path") or []
        print("filtered_path: " + str(self.filtered_path))
        self.load_classes(settings.get("scuggest_import_path"))
        self.process_classes()


    def process_classes(self):
        allEmpty = True
        for sel in self.view.sel():
            if sel.empty():
                wordSel  = self.view.word(sel)
                wordContent = self.view.substr(wordSel)
                if not wordSel.empty() and re.findall("^[a-zA-Z][a-zA-Z0-9]+$", wordContent):
                    self.view.sel().add(wordSel)
                    sel = wordSel
                else:
                    continue
            userSelection = self.view.substr(sel)
            self.process_classes_in_ui(userSelection)

            allEmpty = False

        if allEmpty:
            self.view.window().show_input_panel("Class name: ", "", self.process_classes_in_ui, None, None)

    def match_selection(self, className):
        results = []
        matches = [EndsWithClassNameMatcher(), \
                   EndsWithObjectMatcher(),    \
                   ContainsMatcher(),          \
                   PrefixMatcher(),            \
                   SuffixMatcher(),            \
                   ObjectSubtypesMatcher()]

        print("classesList: " + str(len(self.classesList)))
        count = 0
        for name in self.classesList:
            #skip classes created for functions
            if(name.find("$$anonfun$") != -1 or \
               name.find("$$anon$") != -1 or \
               re.match("^.*\$\d+\.class$", name) or\
               has_element(self.filtered_path, name.startswith)):
                continue

            count = count + 1
            for m in matches:
                if (m.does_match(name, className)):
                    m.add_result(name, className, results)
                    break

        print("classes scanned: " + str(count))
        return sorted(list(set(results)))

    def process_classes_in_ui(self, userSelection):
        results = self.match_selection(userSelection)
        if len(results) == 1:
            self.selectClass(results)(0)
        elif len(results) > 1:
            self.view.window().show_quick_panel(results, self.selectClass(results))
        else:
            sublime.error_message("There is no such class in \"scuggest_import_path\"")

    def selectClass(self, results):
        def withIndex(index):
            if index == -1:
                return
            self.view.run_command("scuggest_add_import_insert", {"classpath":results[index]})

        return withIndex

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