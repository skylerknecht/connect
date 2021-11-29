## Connect
### Versions
 * [1.5](https://github.com/skylerknecht/connect) : 11/28/2021 : python stager, reorganized code base, msbuild, quality of life changes.
 * [1.2](https://github.com/skylerknecht/connect/tree/087006611c8d65f3f3d5fd86bc5ff577a51d1950) : 09/17/2021 : mshta implant code, quality of life changes.
 * [1.0](https://github.com/skylerknecht/connect/tree/33d65a90655c01c92aedd496b9a468512ce83cc9) : 09/11/2021 : jscript options extended.
 * [0.9](https://github.com/skylerknecht/connect/tree/26ab2eb370fc32bf0b443927d7e45e8ffaff2532) : 09/07/2021 : implant results are displayed, information is escaped for communication.
 * [0.8](https://github.com/skylerknecht/connect/tree/17f8861bdefb7426168e036735646f6ca055047d) : 07/02/2021 : modular implants, randomized response data, variable function identifer randomization.
 * [0.3](https://github.com/skylerknecht/connect/tree/c11d1c9934e02e8cd4b5c4a0c5d01136090383e8) : 06/02/2021 : jscript implant code, functional CLI.
 * [0.0](https://github.com/skylerknecht/connect/tree/5816f06aaa96a2a082c9b4afe2454a5ce6b726dd) : 05/11/2021 : initial code base and project structure.

### Features
* [x] Windows and Linux stagers.
* [x] Flask webserver with support for encrypted communications.
* [x] Invalid requests to the Flask webserver will prompt randomized response data.
* [x] Staged files implement randomized identifiers to avoid being signatured.
* [x] MSHTA and JScript functions can be loaded during run time.
* [x] MSHTA and JScript stagers execute C# binaries with MSBuild.

### ToDo
* [ ] Connections maintain system information that is malleable by the operator.

### Verbiage
```
Connection:
  A requested and executed staged file.
  - status: current status of the connection with four possible values.
    - connected (a successfully executed stager)
    - disconnected (connection has not checked in within a thirty minutes.)
    - pending (staged file requested waiting for the first check in)
    - stale (connection has not checked in within one minute)

Stagers:
  Files hosted via an operator defined Flask webserver waiting to be requested and executed.
```

### Using Connect
```sh
./run_connect 127.0.0.1 1337
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
