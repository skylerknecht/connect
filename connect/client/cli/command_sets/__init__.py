from . import agent
from . import tokens
from . import enumeration
from . import execution
from . import files

COMMAND_SETS = [
    tokens.TokenCommands,
    agent.AgentCommands,
    enumeration.EnumerationCommands,
    execution.ExecutionCommands,
    files.FilesCommands
]