from .commands import CommandsManager
from connect.cli.commands.agents import Agent
from .exit import Exit
from .agents import Agent
from .socks import Socks
from .implants import Implant
from .whoami import Whoami

agent = Agent()
exit = Exit()
socks = socks.Socks()
implant = Implant()
whoami = Whoami()


COMMANDS = {
    implant.name: implant,
    whoami.name: whoami,
    socks.name: socks,
    agent.name: agent,
    exit.name: exit
}


