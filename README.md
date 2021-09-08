## Connect
### Versions
 * 0.9 : implant results are displayed, information is escaped for communication
 * 0.8 : modular implants, randomized response data, variable function identifer randomization
 * 0.3 : jscript implant code, functional CLI
 * 0.0 : initial code base and project structure

### Features
* [x] Modular implants. (Implants are extensible through loading functions during run time from discoverable files)
* [x] Randomized response data. (Invalid requests will prompt randomized response data)
* [x] Variable and function indentifer randomization. (Staged files implement randomized identifiers to avoid being signatured)

### ToDo
* [ ] Connection system information properly updates.
* [ ] JScript raw command execution and download files.
* [ ] Allow discoverable files to utilize variables or other dependencies already loaded in a connection.
* [ ] Multiple staged files. (Currently only JScript)

### Documentation
```
Connection:
  A requested staged file.
  - status: current status of the connection with two possible values (sucessfully and pending).
    - pending (staged file requested waiting for first check in)
    - stale (connection has not checked in within 10 seconds)
    - successfull (a successfully executed stager)
    - disconnected (connection has not checked in within a minute)

Stager:
  Payloads hosted via an operator defined Flask webserver waiting to be requested and executed.

Return Codes:
  -3: Mission critical error in exeuction aka Exit.
  -2: Semi critical error in exeuction.
  -1: Informational error in execution.
  0: Impeccable execution.
```

### Using Connect
```sh
./run_connect --ip 127.0.0.1 --port 1337
connect~# pwn pwn pwn
connect~# help

Options
=======

'?': Displays the help menu.
'exit': Exits the current command line.
'help': Displays the help menu.
'verbosity': Toggle verbosity mode on and off.
'version': Display the current application version.

Engine Options
==============

'connections': Displays current connections.
'stagers': Displays staged files ready for delivery.

connect~#
```

### Shoutouts
Thanks to [@Kevin J Clark](https://twitter.com/GuhnooPlusLinux) for all the assitance and inspiration from his sub-par but equally as functional C2... [Badrats](https://gitlab.com/KevinJClark/badrats). (:
