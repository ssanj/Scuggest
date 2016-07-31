Scuggest
==================

Scuggest is a Sublime Text plugin for automatically adding imports to your Scala files. It resolves the package names by scanning through class files either in jar/zip files or in your target directories.

Scuggest was initially based on [JavaImports](https://github.com/MDeiml/SublimeJavaImports) but now works in a completely different way.

Installation
------------

TODO

Usage
-----

First you have to define your `scala_import_path` in your settings.

To add an import either mark all class names to import and press `ctrl+alt+i` or just press `ctrl+alt+i` and then enter the class name.

To add a library to your project, in your `.sublime-project` add
<pre><code>"settings":
{
    "scala_import_path":
    [
        "path/to/library.jar",
        "path/to/targetDir"
    ]
}
</code></pre>