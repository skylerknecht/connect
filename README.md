## Connect
### Versions
 * [2.0](https://github.com/skylerknecht/connect) : 04/13/2022 : refactored the entire code base. sqlite database, tools directory, standalone server, implant comms changed, all features before this don't exist anymore.
 * [1.5](https://github.com/skylerknecht/connect/commit/0b1f038365027d56a54257695a06ef9708b1b684) : 11/28/2021 : python stager, reorganized code base, msbuild, quality of life changes.
 * [1.2](https://github.com/skylerknecht/connect/tree/087006611c8d65f3f3d5fd86bc5ff577a51d1950) : 09/17/2021 : mshta implant code, quality of life changes.
 * [1.0](https://github.com/skylerknecht/connect/tree/33d65a90655c01c92aedd496b9a468512ce83cc9) : 09/11/2021 : jscript options extended.
 * [0.9](https://github.com/skylerknecht/connect/tree/26ab2eb370fc32bf0b443927d7e45e8ffaff2532) : 09/07/2021 : implant results are displayed, information is escaped for communication.
 * [0.8](https://github.com/skylerknecht/connect/tree/17f8861bdefb7426168e036735646f6ca055047d) : 07/02/2021 : modular implants, randomized response data, variable function identifier randomization.
 * [0.3](https://github.com/skylerknecht/connect/tree/c11d1c9934e02e8cd4b5c4a0c5d01136090383e8) : 06/02/2021 : jscript implant code, functional CLI.
 * [0.0](https://github.com/skylerknecht/connect/tree/5816f06aaa96a2a082c9b4afe2454a5ce6b726dd) : 05/11/2021 : initial code base and project structure.

### Using Connect
```sh
~# python -m connect.server <IP> <PORT>
~# python -m connect.client <SERVER_URI> <API_KEY>

connect ~# stagers
```

### Shoutouts
Thanks to [@Kevin Clark](https://twitter.com/GuhnooPlusLinux) for all the assistance and inspiration.
