## Connect
### Versions
 * [2.1](https://github.com/skylerknecht/connect) : 04/28/2022 : csharp implant and usability features for client.
 * [2.0](https://github.com/skylerknecht/connect/commit/c238382658363c7ca81a3e3348c9d1fca74b8d99) : 04/13/2022 : refactored the entire code base. sqlite database, tools directory, standalone server, implant comms changed, all features before this don't exist anymore.
 * [1.5](https://github.com/skylerknecht/connect/commit/0b1f038365027d56a54257695a06ef9708b1b684) : 11/28/2021 : python stager, reorganized code base, msbuild, quality of life changes.
 * [1.2](https://github.com/skylerknecht/connect/tree/087006611c8d65f3f3d5fd86bc5ff577a51d1950) : 09/17/2021 : mshta implant code, quality of life changes.
 * [1.0](https://github.com/skylerknecht/connect/tree/33d65a90655c01c92aedd496b9a468512ce83cc9) : 09/11/2021 : jscript options extended.
 * [0.9](https://github.com/skylerknecht/connect/tree/26ab2eb370fc32bf0b443927d7e45e8ffaff2532) : 09/07/2021 : implant results are displayed, information is escaped for communication.
 * [0.8](https://github.com/skylerknecht/connect/tree/17f8861bdefb7426168e036735646f6ca055047d) : 07/02/2021 : modular implants, randomized response data, variable function identifier randomization.
 * [0.3](https://github.com/skylerknecht/connect/tree/c11d1c9934e02e8cd4b5c4a0c5d01136090383e8) : 06/02/2021 : jscript implant code, functional CLI.
 * [0.0](https://github.com/skylerknecht/connect/tree/5816f06aaa96a2a082c9b4afe2454a5ce6b726dd) : 05/11/2021 : initial code base and project structure.

### Using Connect
```sh
~# python3 -m venv env 
~# source /env/bin/activate

//Install dependencies
(env)~# python3 -m pip install -r requirements.txt

// Run the server
(env)~# python -m connect.server 127.0.0.1 8080
Client Arguments: http://127.0.0.1:8080 123456789

// Run the client the above arguments
(env)~# python -m connect.client http://127.0.0.1:8080 123456789
connect~# stagers

   Type   │             Staged URI           │                    Description                      
╶─────────┼──────────────────────────────────┼────────────────────────────────────────────────────╴
  JScript │ http://127.0.0.1:8080/6179451772 │ A JScript file with a small standard API included.  
  MSBuild │ http://127.0.0.1:8080/9241729871 │  A MSBuild XML file that launches a CSharp agent.
  
// Execute the stager to recieve a succesfull csharp or jscript connection.
connect~# connections
      ID     │  Type   │       Check In       │    Status    │           Username            │    Hostname     │         Operating System           
╶────────────┼─────────┼──────────────────────┼──────────────┼───────────────────────────────┼─────────────────┼───────────────────────────────────╴
  8511453877 │ CSharp  │ 04/28/2022 10:30:53  │  Connected   │ DESKTOP-P1VHEUK\Skyler Knecht │ DESKTOP-P1VHEUK │ Microsoft Windows NT 10.0.19044.0  
 
// Interact with the connection using one of the following commands.
connect~# interact 8511453877
connect~# *8511453877
(8511453877)~# 

// List help menu and schedule jobs with one of the following commands.
(8511453877)~# ?
(8511453877)~# help
(8511453877)~# help -v
[Main Menu]
······································································································
- abbreviated -                                                    
help                  List available commands or provide detailed help for a specific command                                                                

[Standard API]
- abbreviated -                                          
whoami                Retrieve the username of the user.   

(8511453877)~# whoami
[?] Sent whoami job to 8511453877.
[+] whoami job from 8511453877 returned results!
DESKTOP-P1VHEUK\Skyler Knecht
```

### FAQ
* No tab complete on mac? Install gnureadline with pip.

### Shoutouts
Thanks to [@Kevin Clark](https://twitter.com/GuhnooPlusLinux) for all the assistance and inspiration.
