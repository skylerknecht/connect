from . import jscript
from connect.output import Stager

STAGERS = {
    jscript.blueprint: Stager(jscript.blueprint.name, jscript.endpoint,  jscript.delivery)
}
