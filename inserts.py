import re

def get_import_statement(classpath, line):
    # Skip over package declarations and empty lines
    if not re.match("^[\s\t]*package[\s\t]+(?:object)?(?:[\s\t]+)?[a-zA-Z][a-zA-Z0-9]+(?:\.(?:[a-zA-Z][a-zA-Z0-9]+))*$", line) and \
       not re.match("^[\s\t]*$", line):
       importStatement = "import " + classpath

       # If it's a documentation line, then add the import
       #above it and add an extra newline for spacing.
       # if re.match("^[\s\t]*\/\*\*?[\s\t]*.*$", line) or \
       #    re.match("^[\s\t]*\*[\s\t]*.*$", line) or \
       #    re.match("^[\s\t]*\/\/.*$",  line):
       #     importStatementNL = importStatement + "\n\n"
       if re.match("^[\s\t]*import[\s\t]+.*$", line):
         # if it's an import line, then add this import above it
         importStatementNL = importStatement + "\n"
       else:
         # It's not documentation, an empty line or an import;
         # for everything else add the import and two newlines to
         # for some line spacing.
         importStatementNL = importStatement + "\n\n"

       return importStatementNL
    else:
        return None