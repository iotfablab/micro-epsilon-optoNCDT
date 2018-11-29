# micro-epsilon-optoNCDT


Command-Line-Utility written in Python3.x for obtaining information via
Micro-Epsilon's IF1032 ETH Module and OptoNCDT
and storing information to InfluxDB either via UDP or HTTP.


## Installation

clone the repository to your machine and use `pip` to install the CLI:

    pip install .

## Usage


```
    usage: deflection [-h] [--ip IP] [--port PORT] [--http] [--db-host DB_HOST]
                      [--db-port DB_PORT] [--db-name DB_NAME] [--udp]
                      [--udp-port UDP_PORT]

    CLI for acquiring OptoNCDT Sensor and storing it in InfluxDB

    optional arguments:
      -h, --help           show this help message and exit
      --ip IP              IP Address of the IF1032 ETH Module
      --port PORT          Port number for the Stream Server on IF1032 ETH Module
      --http               Send sensor data via HTTP
      --db-host DB_HOST    hostname for InfluxDB HTTP Instance
      --db-port DB_PORT    port number for InfluxDB HTTP Instance
      --db-name DB_NAME    database name to add sensor values to
      --udp                Send sensor data via UDP
      --udp-port UDP_PORT  UDP Port for sending information via UDP. Should also
                           be configured in InfluxDB
```

## Default

if no parameters are provided then the configuration from `/etc/umg/conf.json`
is taken.

    $ deflection # starts socket stream at 192.168.3.201 port 10001 with UDP sending and UDP port 8091

Basic configuration can be found in `conf.json` file. Make sure to either move this file into `/etc` folder.

## Custom
IP address of stream socket is mandatory.

### UDP
1. IP address of the stream socket (mandatory)
2. UDP Port value (mandatory)


    $ deflection --udp --udp-port 20001 --ip 192.168.10.122


### HTTP
1. IP address of stream socket (mandatory)
2. InfluxDB Database Name (mandatory)


    $ deflection --http --db-name test --ip 192.168.10.122



## Maintainer

* Shantanoo Desai (des@biba.uni-bremen.de)
