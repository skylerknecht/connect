from .commands import CommandsManager
from .agents import Agent
from .exit import Exit
from .implants import Implant
from .whoami import Whoami

agent = Agent()
exit = Exit()
implant = Implant()
whoami = Whoami()

COMMANDS = {
    agent.name: agent,
    exit.name: exit,
    implant.name: implant,
    whoami.name: whoami
}


