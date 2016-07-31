import sublime, sublime_plugin
import zipfile
import os

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
                classesList.append((root + os.sep + filename)[len(path):])
        return classesList

class JavaAddImportCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print("========> updated version")
        settings = self.view.settings()
        if not settings.has("java_import_path"):
            settings = sublime.load_settings("JavaImports.sublime-settings")
            if not settings.has("java_import_path"):
                sublime.error_message("You must first define \"java_import_path\" in your settings")
                return
        if len(settings.get("java_import_path")) == 0:
            sublime.error_message("You must first define \"java_import_path\" in your settings")
            return
        classesList = []
        for path in settings.get("java_import_path"):
            classesList = classesList + get_classes_list(path)

        def onDone(className):
            results = []
            print("called with: " + className)

            for name in classesList:
                if  name.endswith(os.sep + className + ".class"):
                    result = name.replace(os.sep, ".").replace(".class", "")
                    if result.startswith("."):
                        result = result[1:]
                    results.append(result)
                elif name.endswith("$" + className + "$.class"):
                    result = name.replace(os.sep, ".").replace("$", ".").replace("..class", "")
                    if result.startswith("."):
                        result = result[1:]
                    results.append(result)
                elif className.startswith("*") and className.endswith("*") and name.find("$") == -1 and len(className) > 4:
                     startIndex = name.rfind ( os.sep )
                     endIndex = name.rfind(".")
                     toMatch = className[1:][:-1]
                     if startIndex != -1 and endIndex != -1 and \
                        (name.find(toMatch, startIndex - endIndex) != -1):
                        result = name.replace(os.sep, ".").replace(".class", "")
                        if result.startswith("."):
                            result = result[1:]
                        results.append(result)
                elif className.endswith("*") and name.find("$") == -1 and len(className) > 4:
                     startIndex = name.rfind ( os.sep )  + 1
                     toMatch = className[:-1]
                     if startIndex != -1 and \
                        (name.find(toMatch, startIndex, startIndex + len(toMatch)) != -1):
                        result = name.replace(os.sep, ".").replace(".class", "")
                        if result.startswith("."):
                            result = result[1:]
                        results.append(result)
                elif className.startswith("*") and name.find("$") == -1 and len(className) > 4:
                     endIndex = name.rfind(".")
                     toMatch = className[1:]
                     if endIndex != -1 and \
                        (name.find(toMatch, endIndex - len(toMatch), endIndex) != -1):
                        result = name.replace(os.sep, ".").replace(".class", "")
                        if result.startswith("."):
                            result = result[1:]
                        results.append(result)

            def finishUp(index):
                if index == -1:
                    return
                self.view.run_command("java_add_import_insert", {"classpath":results[index]})

            if len(results) == 1:
                finishUp(0)
            elif len(results) > 1:
                self.view.window().show_quick_panel(results, finishUp)
            else:
                sublime.error_message("There is no such class in \"java_import_path\"")

        allEmpty = True
        for sel in self.view.sel():
            if sel.empty():
                continue
            onDone(self.view.substr(sel))
            allEmpty = False
        if allEmpty:
            self.view.window().show_input_panel("Class name: ", "", onDone, None, None)

class JavaAddImportInsertCommand(sublime_plugin.TextCommand):
        def run(self, edit, classpath):
            for i in range(0,10000):
                point = self.view.text_point(i,0)
                region = self.view.line(point)
                line = self.view.substr(region)
                if "import" in line or "class" in line:
                    self.view.insert(edit,point,"import " + classpath + "\n")
                    break