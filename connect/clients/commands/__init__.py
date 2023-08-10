from .commands import CommandsManager
from .exit import Exit
from .implant import Implant

exit = Exit()
implant = Implant()

COMMANDS = {
    exit.name: exit,
    implant.name: implant
}

commands_manager = CommandsManager(COMMANDS)
