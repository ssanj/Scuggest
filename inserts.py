import re

def get_import_statement(classpath, line):
    # Skip over package declarations and empty lines
    if not re.match("^[\s\t]*package[\s\t]+(?:object)?(?:[\s\t]+)?[a-zA-Z][a-zA-Z0-9]+(?:\.(?:[a-zA-Z][a-zA-Z0-9]+))*$", line) and \
       not re.match("^[\s\t]*$", line):
       importStatement = "import " + classpath

       # if it's an import line, then add this import above it.
       if re.match("^[\s\t]*import[\s\t]+.*$", line):
         importStatementNL = importStatement + "\n"
       else:
         # It's not a package or an empty line or an import.
         # For everything else add the import and two newlines
         # for some line spacing, between the import and whatever
         # comes next.
         importStatementNL = importStatement + "\n\n"

       return importStatementNL
    else:
        return None