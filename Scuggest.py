import sublime, sublime_plugin
import zipfile
import os
import re

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

class ScuggestAddImportCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = self.view.settings()
        if not settings.has("scuggest_import_path"):
            settings = sublime.load_settings("Scuggest.sublime-settings")
            if not settings.has("scuggest_import_path"):
                sublime.error_message("You must first define \"scuggest_import_path\" in your settings")
                return
        if len(settings.get("scuggest_import_path")) == 0:
            sublime.error_message("You must first define \"scuggest_import_path\" in your settings")
            return
        classesList = []
        for path in settings.get("scuggest_import_path"):
            classesList = classesList + get_classes_list(path)
            classesList = list(map(lambda x: x.replace("\\", "/"), classesList))

        def addResults(results, result):
            if result.startswith("."):
                result = result[1:]
            results.append(result)

        def onDone(className):
            results = []
            print("called with: " + className)

            for name in classesList:
                # classes that end with className. Eg: java.util.UUID
                if  name.endswith("/" + className + ".class"):
                    result = name.replace("/", ".").replace(".class", "")
                    addResults(results, result)
                # nested className. Eg: Outer.className
                elif name.endswith("$" + className + "$.class"):
                    result = name.replace("/", ".").replace("$", ".").replace("..class", "")
                    addResults(results, result)
                elif className.startswith("*") and className.endswith("*") and name.find("$") == -1 and len(className) > 4:
                     startIndex = name.rfind ( "/" )
                     endIndex = name.rfind(".")
                     toMatch = className[1:][:-1]
                     if startIndex != -1 and endIndex != -1 and \
                        (name.find(toMatch, startIndex - endIndex) != -1):
                        result = name.replace("/", ".").replace(".class", "")
                        addResults(results, result)
                elif className.endswith("*") and name.find("$") == -1 and len(className) > 4:
                     startIndex = name.rfind ( "/" )  + 1
                     toMatch = className[:-1]
                     if startIndex != -1 and \
                        (name.find(toMatch, startIndex, startIndex + len(toMatch)) != -1):
                        result = name.replace("/", ".").replace(".class", "")
                        addResults(results, result)
                elif className.startswith("*") and name.find("$") == -1 and len(className) > 4:
                     endIndex = name.rfind(".")
                     toMatch = className[1:]
                     if endIndex != -1 and \
                        (name.find(toMatch, endIndex - len(toMatch), endIndex) != -1):
                        result = name.replace("/", ".").replace(".class", "")
                        addResults(results, result)
                elif name.endswith("/" + className +"$.class"):
                    result = name.replace("/", ".").replace("$.class", "._")
                    addResults(results, result)

            def finishUp(index):
                if index == -1:
                    return
                self.view.run_command("scuggest_add_import_insert", {"classpath":results[index]})

            if len(results) == 1:
                finishUp(0)
            elif len(results) > 1:
                self.view.window().show_quick_panel(results, finishUp)
            else:
                sublime.error_message("There is no such class in \"scuggest_import_path\"")

        allEmpty = True
        for sel in self.view.sel():
            if sel.empty():
                continue
            onDone(self.view.substr(sel))
            allEmpty = False
        if allEmpty:
            self.view.window().show_input_panel("Class name: ", "", onDone, None, None)

class ScuggestAddImportInsertCommand(sublime_plugin.TextCommand):
        def run(self, edit, classpath):
            for i in range(0,10000):
                point = self.view.text_point(i,0)
                region = self.view.line(point)
                line = self.view.substr(region)
                if line.startswith("import ") or \
                   line.startswith("class ") or \
                   line.startswith("trait ") or \
                   line.startswith("object "):
                    self.view.insert(edit,point,"import " + classpath + "\n")
                    break