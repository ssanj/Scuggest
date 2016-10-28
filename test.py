import unittest
from inserts import *

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.classpath = "some.artifact.Artifact"

    def test_get_import_statement_with_package(self):
        self.assertEqual(get_import_statement(self.classpath, "package blah.de.blah"), None)
        self.assertEqual(get_import_statement(self.classpath, "package object blah"), None)

    def test_get_import_statement_with_empty_line(self):
        self.assertEqual(get_import_statement(self.classpath, ""), None)
        self.assertEqual(get_import_statement(self.classpath, " "), None)
        self.assertEqual(get_import_statement(self.classpath, "          "), None)

    def test_get_import_statement_with_import(self):
        line = "import scala.concurrent.Future"
        self.assertEqual(get_import_statement(self.classpath, line), "import some.artifact.Artifact\n")

    def test_get_import_statement_with_scaladoc(self):
        self.assertEqual(get_import_statement(self.classpath, "/** This is some scaladoc"),
            "import some.artifact.Artifact\n\n")
        self.assertEqual(get_import_statement(self.classpath, "* more doc"),
            "import some.artifact.Artifact\n\n")

    def test_get_import_statement_with_comment(self):
        self.assertEqual(get_import_statement(self.classpath, "// single line comment"),
            "import some.artifact.Artifact\n\n")

    def test_get_import_statement_with_entities(self):
        entities = ["trait Blah",
                    "object Blee",
                    "class Blob",
                    "abstract class Been",
                    "case class Bloom",
                    "final class Bling",
                    "sealed trait Bongo"
                   ]
        for e in entities:
            self.assertEqual(get_import_statement(self.classpath, e),
                "import some.artifact.Artifact\n\n")

if __name__ == '__main__':
    unittest.main()