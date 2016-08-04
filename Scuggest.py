import sublime, sublime_plugin
import zipfile
import os
import re

class Results:
    @classmethod
    def add(self, results, result):
        if result.startswith("."):
            result = result[1:]
        if result.endswith("."):
            result = result[:-1]

        results.append(result)

# example: /net/ssanj/dabble/ResolverParser.class
# search: ResolverParser
class EndsWithClassNameMatcher:

    def name(self):
        return "ends_with_class_name_matcher"

    def does_match(self, filename, className):
        return filename.endswith("/" + className + ".class")

    def add_result(self, filename, className, results):
        result = filename.replace("/", ".").replace(".class", "")
        Results.add(results, result)

# example: /net/ssanj/dabble/DabblePathTypes$DabbleWorkPath$.class
# search: DabbleWorkPath
class EndsWithObjectMatcher:

    def name(self):
        return "ends_with_object_matcher"

    def does_match(self, filename, className):
        return filename.endswith("$" + className + "$.class")

    def add_result(self, filename, className, results):
        result = filename.replace("/", ".").replace("$", ".").replace(".class", "")
        Results.add(results, result)

# example: /com/sun/corba/se/spi/orbutil/threadpool/NoSuchWorkQueueException
# search: *Work*
class ContainsMatcher:

    def name(self):
        return "contains_matcher"

    def is_wildcard(self, filename, className):
        startIndex = filename.rfind( "/" )
        endIndex   = filename.rfind(".")
        toMatch    = className[1:][:-1]
        return startIndex != -1 and \
               endIndex != -1 and \
               (filename.find(toMatch, startIndex, startIndex + endIndex) != -1)

    def does_match(self, filename, className):
        return className.startswith("*") and \
               className.endswith("*") and \
               len(className) > 4 and \
               self.is_wildcard(filename, className)

    def add_result(self, filename, className, results):
            result = filename.replace("/", ".").replace("$", ".").replace(".class", "")
            Results.add(results, result)

# example: java.sql.PreparedStatement
# search: Prepared*
class PrefixMatcher:

    def name(self):
        return "prefix_matcher"

    def is_wild_card(self, filename, className):
        startIndex = filename.rfind ( "/" )  + 1
        toMatch = className[:-1]
        return startIndex != -1 and \
               (filename.find(toMatch, startIndex, startIndex + len(toMatch)) != -1)

    def does_match(self, filename, className):
        return className.endswith("*") and \
               len(className) > 4 and \
               self.is_wild_card(filename, className)

    def add_result(self, filename, className, results):
        result = filename.replace("/", ".").replace("$", ".").replace(".class", "")
        Results.add(results, result)

# example: java.time.ZonedDateTime
# search *DateTime
class SuffixMatcher:

    def name(self):
        return "suffix_matcher"

    def is_wild_card(self, filename, className):
        endIndex = filename.rfind(".")
        toMatch  = className[1:]
        return endIndex != -1 and \
               (filename.find(toMatch, endIndex - len(toMatch), endIndex) != -1)

    def does_match(self, filename, className):
        return className.startswith("*") and \
               len(className) > 4 and \
               self.is_wild_card(filename, className)

    def add_result(self, filename, className, results):
        result = filename.replace("/", ".").replace("$", ".").replace(".class", "")
        Results.add(results, result)

# example: /net/ssanj/dabble/DabblePathTypes.DabbleWorkPath.NestedDabbleWorkPath.MoreNestedDabbleWorkPath
# search: DabbleWorkPath
# results:
#  net.ssanj.dabble.DabblePathTypes.DabbleWorkPath
#  net.ssanj.dabble.DabblePathTypes.DabbleWorkPath.NestedDabbleWorkPath
#  net.ssanj.dabble.DabblePathTypes.DabbleWorkPath.NestedDabbleWorkPath.MoreNestedDabbleWorkPath
#  net.ssanj.dabble.DabblePathTypes.DabbleWorkPath._
class ObjectSubtypesMatcher:

    def name(self):
        return "object_subtypes_matcher"

    def does_match(self, filename, className):
        return((len(re.findall(r"/"   + className + "\$.+\.class", filename)) != 0) or \
              (len(re.findall(r"/(.+\$)" + className + "(\$.+)*\.class", filename))))

    def add_result(self, filename, className, results):
        startIndex = filename.rfind("/") + 1
        length     = len(filename) - len(".class")
        evaluate   = filename[startIndex: length]
        prefix     = filename[:startIndex].replace("/", ".")

        # there are instances of className$class.class, so skip the extra class
        segments = [s for s in evaluate.split("$") if len(s) > 0 and s != "class"]

        for s in segments:
            if (s == className):
                # print("prefix: " + prefix)
                # print("segments: " + str(segments))
                # print("filename: " + filename)
                result = prefix + ".".join(segments)
                Results.add(results, result)

                # if it's a parent then add ._
                if (segments[-1] != className):
                    valueIndex = segments.index(className) + 1
                    wildcard = prefix + ".".join(segments[:valueIndex]) + "._"
                    Results.add(results, wildcard)

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
        debug = True
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
            matches = [EndsWithClassNameMatcher(), \
                       EndsWithObjectMatcher(),    \
                       ContainsMatcher(),          \
                       PrefixMatcher(),            \
                       SuffixMatcher(),            \
                       ObjectSubtypesMatcher()]

            for name in classesList:
                #skip classes created for functions
                if(name.find("$$anonfun$") != -1):
                    continue

                for m in matches:
                    if (m.does_match(name, className)):
                        m.add_result(name, className, results)
                        break

            def finishUp(index):
                if index == -1:
                    return
                self.view.run_command("scuggest_add_import_insert", {"classpath":results[index]})

            results = sorted(list(set(results)))
            if len(results) == 1:
                finishUp(0)
            elif len(results) > 1:
                self.view.window().show_quick_panel(results, finishUp)
            else:
                sublime.error_message("There is no such class in \"scuggest_import_path\"")

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