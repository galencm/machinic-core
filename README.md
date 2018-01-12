# README

## Overview

The core machine provides necessary **routing**, **interconnectivity** and **state** functionality. 

* Routing:
    * Mosquitto pubsub (bridged to redis for routing)
    * Redis pubsub
    * Routling dsl for message parsing and flexible routing
    * Pipeling dsl for dataflows 
* Wireless Interconnectivity:
    * Access point created with host-ap
    * Identify and configure wireless devices based on framework(s)(using Homie)
* State:
    * Redis 

## Quickstart
* Consul & nomad must be running
* see [machinic-env](https://github.com/galencm/machinic-env) for setup scripts

clone repos:
```
git clone https://github.com/galencm/machinic-core
git clone https://github.com/galencm/ma
```
use ma/machinic to generate start/stop scripts:
```
cd ma/machinic
python3 machine.py generate --name machine_core --file ~/machinic-core/machine.yaml
```
run start script and tests:
```
cd ~/machinic-core
./start.sh
pytest -v
```

## Contributing

This project uses the C4 process 

[https://rfc.zeromq.org/spec:42/C4/](https://rfc.zeromq.org/spec:42/C4/)

##  <a name="license"></a> License
Mozilla Public License, v. 2.0 

[http://mozilla.org/MPL/2.0/](http://mozilla.org/MPL/2.0/)


