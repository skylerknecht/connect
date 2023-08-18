from .implants import Implant
from .whoami import Whoami

implant = Implant()
whoami = Whoami()


COMMANDS = {
    implant.name: implant,
    whoami.name: whoami
}