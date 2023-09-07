from .agents import Agent
from .arch import Arch
from .bypause import ByPause
from .dir import Dir
from .drives import Drives
from .download import Download
from .execute_assembly import ExecuteAssembly
from .exit import Exit
from .hostname import Hostname
from .implants import Implant
from .integrity import Integrity
from .ip import IP
from .os import OS
from .pid import PID
from .pwd import PWD
from .shell import Shell
from .spawn import Spawn
from .upload import Upload
from .whoami import Whoami

agent = Agent()
arch = Arch()
bypause = ByPause()
dir = Dir()
drives = Drives()
download = Download()
execute_assembly = ExecuteAssembly()
exit = Exit()
hostname = Hostname()
implant = Implant()
integrity = Integrity()
ip = IP()
os = OS()
pid = PID()
pwd = PWD()
shell = Shell()
spawn = Spawn()
upload = Upload()
whoami = Whoami()

COMMANDS = {
    agent.name: agent,
    arch.name: arch,
    bypause.name: bypause,
    dir.name: dir,
    drives.name: drives,
    download.name: download,
    execute_assembly.name: execute_assembly,
    exit.name: exit,
    hostname.name: hostname,
    implant.name: implant,
    integrity.name: integrity,
    ip.name: ip,
    os.name: os,
    pid.name: pid,
    pwd.name: pwd,
    shell.name: shell,
    spawn.name: spawn,
    upload.name: upload,
    whoami.name: whoami
}
