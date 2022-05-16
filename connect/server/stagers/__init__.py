from . import jscript
from . import csharp
from connect.output import Stager

STAGERS = {
    jscript.blueprint: Stager(jscript.blueprint.name, jscript.endpoint,  jscript.delivery),
    csharp.blueprint: Stager(csharp.blueprint.name, csharp.endpoint,  csharp.delivery)
}
