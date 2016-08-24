import zipfile
import os
import re

class Results:
    extra_dots = re.compile("(\.){2,}")

    @classmethod
    def add(self, results, result):
        if result.startswith("."):
            result = result[1:]
        if result.endswith("."):
            result = result[:-1]

        #remove `package` from package path.
        result = result.replace(".package", "")

        #remove any duplicate dots.
        #eg. path/$blah -> path..blah
        result = re.sub(Results.extra_dots, ".", result)
        # result = result.replace("..", "")

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

# example: /com/sun/corba/se/spi/orbutil/threadpool/NoSuchWorkQueueException.class
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