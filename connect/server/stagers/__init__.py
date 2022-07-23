from . import jscript
from . import csharp
from connect.output import Stager

STAGERS = {
    jscript.blueprint: Stager(jscript.blueprint.name, jscript.endpoints),
    csharp.blueprint: Stager(csharp.blueprint.name, csharp.endpoints),
}
