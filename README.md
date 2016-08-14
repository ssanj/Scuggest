Scuggest
========

Scuggest (pronounced 'Suggest') is a Sublime Text plugin for automatically adding imports to your Scala files. It resolves the class names by scanning through a provided list of jar or class directories.

Scuggest was initially based on [JavaImports](https://github.com/MDeiml/SublimeJavaImports) but now works in a completely different way.

Installation
------------

Here are a few ways to install Scuggest on your system.

1. The easiest way to install Scuggest is through [Package Control](https://packagecontrol.io/packages/Scuggest).

2. Git clone the Scuggest repository into your Packages directory:

```git clone git@github.com:ssanj/Scuggest.git```

3. Download the [latest release](https://github.com/ssanj/Scuggest/releases) source code and extract it to the Packages directory.

> The Packages directory is located at:

> * OS X: ~/Library/Application Support/Sublime Text 3/Packages
> * Linux: ~/.config/sublime-text-3/Packages
> * Windows: %APPDATA%\Sublime Text 3\Packages

Configuration
--------------

To use Scuggest, you need to have a project file (.sublime-project) created for your Scala project. You can do this for an existing project by clicking on the __Project__ > __Save Project As ...__ menu item and saving the project to the root of your Scala project directory.

Once you have a project created, here is an example settings element:

```javascript
"settings": {
        "scuggest_import_path":
        [
            "/Library/Java/JavaVirtualMachines/jdk1.8.0_65.jdk/Contents/Home/jre/lib/rt.jar",
            "/Users/sanj/.ivy2/cache/org.scala-lang/scala-library/jars/scala-library-2.11.8.jar",
            "/Volumes/Work/projects/code/scala/toy/dabble/target/scala-2.11/classes",
            "/Users/sanj/.ivy2/cache/com.lihaoyi/ammonite-ops_2.11/jars/ammonite-ops_2.11-0.5.7.jar",
            "/Users/sanj/.ivy2/cache/com.github.scopt/scopt_2.11/jars/scopt_2.11-3.4.0.jar",
            "/Users/sanj/.ivy2/cache/org.scalaz/scalaz-core_2.11/jars/scalaz-core_2.11-7.2.2.jar"
        ],
        "scuggest_filtered_path":
        [
            "com/sun",
            "sun",
            "javax/swing",
            "org/omg",
            "com/apple",
            "java/awt"
        ]
}
```

__scuggest_import_path__ lists the jar files you want Scuggest to look for classes in. This can include either Java or Scala jar files. Some typical jars to include are the Java rt.jar file and the scala-library-scala-version.jar file. You can add as many or as few libraries that you want searched here.

__scuggest_filtered_path__ lists the path prefixes that are skipped when scanning for a target class. A typical example could be anything under the com/sun package. Notice that these are file path as opposed to package (or dotted) paths.

Usage
-----

You can use Scuggest in the following ways:

1. Click on the name of a class that you want to import into your Scala source file and press __ALT + CMD + I__. This will select the word under the cursor and attempt to display any matched classes.

![Scuggest importing a class](scuggest_import_720.mov.gif)

2. You can also manually select multiple class names and then press __ALT + CMD + I__ to import them all. You will be given a list of matches for each selection.

3. If you press __ALT + CMD + I__ on an empty line then a search box will be displayed allowing you to enter the class name or a wildcard to match on.

![Scuggest importing a class](scuggest_wildcard_import_720.mov.gif)

Selection Matchers
------------------

### 1. class name ###

This is the first matcher that is tried against a selection. It attempts to find classes that ends with the search term supplied.
_NB_ A selection is converted to a search term. The actual matching is done against the search terms.

```
# example class: net.ssanj.dabble.ResolverParser.class
# search term: ResolverParser
# matched: true
```

```
# example class: net.ssanj.dabble.DabbleWorkPath.class
# search term: ResolverParser
# matched: false
```

```
# example class: net.ssanj.dabble.ResolverParser.class
# search term: ResolverPars
# matched: false
```

### 2. Object name ###

This is similar to the __Ends with class name__ matcher but only matches objects that end with search term.

```
# example: net.ssanj.dabble.DabblePathTypes$DabbleWorkPath$.class
# search term: DabbleWorkPath
# match: true
```

### 3. Object with subtype(s) ###

Matches a search term against and object that defines other types (classes, traits or other objects)

```
# example: net.ssanj.dabble.DabblePathTypes.DabbleWorkPath.NestedDabbleWorkPath.MoreNestedDabbleWorkPath
# search term: DabbleWorkPath
# matches:
#  net.ssanj.dabble.DabblePathTypes.DabbleWorkPath
#  net.ssanj.dabble.DabblePathTypes.DabbleWorkPath.NestedDabbleWorkPath
#  net.ssanj.dabble.DabblePathTypes.DabbleWorkPath.NestedDabbleWorkPath.MoreNestedDabbleWorkPath
#  net.ssanj.dabble.DabblePathTypes.DabbleWorkPath._
```

Wildcard Matches
----------------

These matchers are generally used through a search box.

### 1. By prefix

Matches a class name that starts with the given search term. The search term should end with an __*__.

```
# search term: Future*
# matches:
#   java.util.concurrent.Future
#   java.util.concurrent.FutureTask
#   scala.concurrent.Future
#   scala.concurrent.FutureTaskRunner
```

### 2. By suffix

Matches a class name that ends with the given search term. The search term should end with an __*__.

```
# search *DateTime
# matches:
#  java.time.LocalDateTime
#  java.time.OffsetDateTime
#  java.time.ZonedDateTime
#  java.time.chrono.ChroLocalDateTime
#  java.time.chrono.ChroZonedDateTime
#  java.util.Formatter.DateTime
```

### 3. Anywhere

Matches the supplied search term anywhere in the class name. The search term should begin and end with an __*__.

```
# search: *Work*
# matches:
#  java.util.concurrent.ForkJoinWorkerThread
#  java.util.concurrent.ForkJoinPool.WorkQueue
#  java.util.concurrent.ForkJoinPool.InnocuousForkJoinWorkerThreadFactory
#  java.util.concurrent.ForkJoinPool.ForkJoinWorkerThreadFactory
#  java.util.concurrent.ForkJoinPool.DefaultForkJoinWorkerThreadFactory

```