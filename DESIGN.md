# Design

## Current

1. This plugin will only return Class/Trait names. It will not return method names.
1. Class names are matched directly with the selection.
1. Searches through source and class variants.
1. Only handles zip files.


## Next

1. Search through directories. [x]
1. Fuzzy matching on class names.
    Prepared* -> java.sql.PreparedStatement [x]
    *Spec -> org.scalatest.{FlatSpec, FunSpec ...} [x]
    *Path* -> XYZPathDsl, SomethingPath, PathSomething [x]
1. Fuzzy match should support nested class definitions
1. separate out test from production dependencies => may need Scoggle paths
1. specify packages to search through:
    ammonite:Path,
    scalatest: *Spec
1. Support for nested class definitions: [x]
    net/ssanj/dabble/DabbleDslDef$FileExists$.class =>
     Should still find FileExits
        net.sanj.dabble.DabbleDslDef.FileExists
1. Auto add project class files
1. Auto add project dependency jars files
1. Auto add java src files