#!/usr/bin/env python3
# Python3 Command Line Utility to read from OptoNCDT sensor connected to
# Micro-Epsilon's IF1032 ETH Module. This Script reads from a Stream Socket
# from the Module at port 10001 (default), converts the raw value to metric values
# and stores the information in InfluxDB via either UDP or HTTP
# Author: Shantanoo Desai <des@biba.uni-bremen.de>

import sys
import struct
import socket
import logging
import json
import argparse
import time
import datetime
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError

# Logger Settings
logger = logging.getLogger("main")
logger.setLevel(logging.ERROR)

handler = logging.FileHandler("/tmp/deflection.log")
handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s-%(name)s-%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


CONF_PATH = '/etc/umg/conf.json'

# Constants for Conversion
DRANGEMAX = 0
DRANGEMIN = 0
MEASRANGE = 0
OFFSET = 0

# socket
sock = None

# InfluxDB Client
client = None

def raw_to_mm(raw_val):
    global DRANGEMAX, DRANGEMIN, MEASRANGE, OFFSET
    return float(((raw_val - DRANGEMIN) * MEASRANGE) / (DRANGEMAX - DRANGEMIN) + OFFSET)

def send_data(ip, port, db_host, db_port, db_name, use_udp, udp_port):
    """Main Function to read from Stream Socket, Convert Raw value to Metric,
       and store it in InfluxDB via UDP/HTTP
    """
    # print(ip, port, db_host, db_port, use_udp, udp_port)
    global client
    if use_udp:
        """use UDP to send Data to InfluxDB"""
        # create UDP Specific client to InfluxDB
        try:
            client = InfluxDBClient(host=db_host, port=db_port, use_udp=True, udp_port=udp_port)
            logger.info('InfluxDB Client Created for UDP Sending')
        except InfluxDBClientError as e:
            logger.exception('Exception while InfluxDB Client Creation for UDP')
            raise(e)
            sys.exit(2)

        # Dict layout for sending Data via UDP to InfluxDB
        measurement = {
            "tags":{
                "loc": "hull"
            },
            "points": [
                {
                    "measurement": "deflection",
                    "fields": {
                        "value": 0.0,
                        "status": 0
                    }
                }
            ]
        }

    else:
        """use HTTP to send Data to InfluxDB"""
        # create HTTP Specific client to InfluxDB
        try:

            client = InfluxDBClient(host=db_host, port=db_port, use_udp=False, database=db_name)
            logger.info('InfluxDB Client Created for HTTP Sending')
        except InfluxDBClientError as e:
            logger.exception('Exception while InfluxDB Client Creation for HTTP')
            raise(e)
            sys.exit(2)

        # Dict layout for sending Data via HTTP to InfluxDB
        measurement = [
            {
                "measurement": "deflection",
                "tags": {
                    "loc": "hull"
                },
                "fields": {
                    "value": 0.0,
                    "status": 0
                }
            }
        ]
    try:
        # Create a TCP/IP socket
        global sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info('Stream Socket Created for Reading')

        server_address = (ip, port)
        logger.debug('connecting to %s port %s' % server_address)
        sock.connect(server_address)
    except socket.error as e:
        logger.exception('Exception while Creating Stream Socket at %s, %s' % server_address)
        raise(e)
        sys.exit(2)


    while True:
        raw_sensor_val = 0
        # read raw values from Stream Socket
        data = sock.recv(44)
        if len(data) == 44:
            # Unpack 44 Bytes worth of data according to IF1032's Manual
            preamble, article, serial, x1, x2, status, bpf, mValCounter, CH1, CH2, CH3 = struct.unpack('<4sIIQHhIIIII', data)

        if preamble == b'SAEM' and len(data) == 44:
            # Current Setting provides values on Channel 3
            raw_sensor_val = CH3
            if use_udp:
                # send data using UDP
                measurement["points"][0]["fields"]["value"] = raw_to_mm(raw_sensor_val)
                measurement["time"] = time.time()
                logger.debug(measurement)
                try:
                    client.send_packet(measurement)
                except InfluxDBClientError as e:
                    logger.exception('Exception during sending data with UDP')
                    raise(e)
                    sys.exit(3)
            else:
                # send data using HTTP
                measurement[0]["fields"]["value"] = raw_to_mm(raw_sensor_val)
                measurement[0]["time"] = datetime.datetime.isoformat('T') + 'Z'
                logger.debug(measurement)
                try:
                    client.write_points(measurement)
                except InfluxDBClientError as e:
                    logger.exception('Exception during sending data with HTTP')
                    raise(e)
                    sys.exit(3)



def parse_args():
    """Parse Arguments if Passed else use configuration file"""

    parser = argparse.ArgumentParser(description='CLI for acquiring OptoNCDT Sensor and storing it in InfluxDB')


    parser.add_argument('--ip', type=str, required=False, help='IP Address of the IF1032 ETH Module')

    parser.add_argument('--port', type=int, required=False, default=10001,
                        help='Port number for the Stream Server on IF1032 ETH Module. Default: 10001')

    parser.add_argument('--http', dest='udp', action='store_false', default=False,
                        help='Send sensor data via HTTP. Default: Disabled')

    parser.add_argument('--db-host', type=str, required=False, default='localhost',
                        help="hostname for InfluxDB HTTP Instance. Default: localhost")

    parser.add_argument('--db-port', type=int, required=False, default=8086,
                        help='port number for InfluxDB HTTP Instance. Default: 8086')

    parser.add_argument('--db-name', type=str, required=False,
                        help='database name to add sensor values to')

    parser.add_argument('--udp', dest='udp', action='store_true', default=True,
                        help='Send sensor data via UDP. Default: Enabled')

    parser.add_argument('--udp-port', type=int, required=False,
                        help='UDP Port for sending information via UDP. \nShould also be configured in InfluxDB')

    parser.set_defaults(udp=True)

    return parser.parse_args()



def main():
    args = parse_args() # parse the arguments
    CONF = dict() # create Dict for Configuration

    with open(CONF_PATH) as cFile:
        _conf = json.load(cFile)
        CONF = _conf['NCDT'] # store conf for NCDT

    # Store all Conversion Variables
    global DRANGEMAX, DRANGEMIN, MEASRANGE, OFFSET
    DRANGEMAX = CONF['conversion']['DRANGEMAX']
    DRANGEMIN = CONF['conversion']['DRANGEMIN']
    MEASRANGE = CONF['conversion']['MEASRANGE']
    OFFSET = CONF['conversion']['OFFSET']
    print(DRANGEMAX, DRANGEMIN, MEASRANGE, OFFSET)

    if len(sys.argv) == 1:
        # Default script execution
        logger.debug('Starting Script in Default Mode. Reading Conf File in %s' %CONF_PATH)
        logger.debug(json.dumps(CONF))
        try:
            send_data(ip=CONF['IP'],
            port=args.port,
            db_host=args.db_host,
            db_port=args.db_port,
            db_name= args.db_name,
            use_udp=args.udp,
            udp_port=CONF['dbConf']['udp_port']
            )

        except KeyboardInterrupt as e:
            logger.exception('CTRL+C hit for Default Configuration')
            client.close()
            sock.close()
            sys.exit(0)

    elif len(sys.argv) > 1:
        if args.ip is None:
            print('No IP of Stream Socket Mentioned. Please Provide IP address using --ip')
            sys.exit(1)
        if args.udp and args.udp_port == None:
                print('No UDP Port Mentioned. Please provide UDP Port using --udp-port')
                sys.exit(1)

        elif not args.udp and args.db_name == None:
                print('No DB Name Mentioned. Please provide DB Name using --db-name')
                sys.exit(1)
        else:
            print('Starting Script with Custom Arguments.')
            logger.debug('starting with custom arguments')
            if args.udp:
                logger.debug('conf: ' + json.dumps({'ip': args.ip, 'udp_port': args.udp_port}))
            logger.debug('conf: ' + json.dumps({'ip': args.ip, 'db-name': args.db_name}))
            try:
                send_data(ip=args.ip,
                port=args.port,
                db_host=args.db_host,
                db_port=args.db_port,
                db_name=args.db_name,
                use_udp=args.udp,
                udp_port=args.udp_port
                )
            except KeyboardInterrupt as e:
                client.close()
                sock.close()
                sys.exit(0)

if __name__ == '__main__':
    main()
