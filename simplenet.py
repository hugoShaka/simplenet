#!/usr/bin/env python3

"""
Spins up a virtual switch to bridge eth ports.
Can setup a dhcp server and a nat.

Usage:
  simplenet switch [--name NAME] <interface>...
  simplenet switch [--name NAME] --with-ip [--ip IP --range RANGE] [--dhcp] <interface>...
  simplenet nat <bridge> <destination>
  simplenet clean [--name NAME] [--except=<exception>]...
  simplenet -h | --help
  simplenet --version

Options:
    -h, --help          Print this help and exit.
    -n, --name NAME    Name of the bridge [default: br0]
    -e, --except <exception>...       Do not touch this interface
    -i, --ip IP        Machine ip on the bridge [default: 192.168.2.2]
    -r, --range RANGE       Subnet of the bridge [default: 192.168.2.0/24]
    -w, --with-ip           Connect the current machine to the bridged network

Arguments:
    interface     Interface you want to add
    bridge        Bridge to operate on
    destination   Interface where we'll NAT behind
"""


import logging

from logging.handlers import RotatingFileHandler

import docopt


def checks():
    """ Do the checks :
    - is bridge-utils available
    - are we root
    - do we have IPs """
    log = logging.getLogger()
    log.info("Running checks")


def switch(name, interfaces):
    """ Setup a virtual switch on given ports.
    Can get tha machine an IP and setup a DHCP server
    """
    log = logging.getLogger()
    log.info("Creating switch %s linking %r", name, interfaces)


def nat():
    """Sets up a NAT"""
    log = logging.getLogger()
    log.info("Creating Nat")
    raise NotImplementedError("Nat not implemented")


def dhcp():
    """Sets up a DHCP server on a given bridge for a given ip range"""
    log = logging.getLogger()
    log.info("Creating DHCP server")


def clean():
    """Clean our shit"""
    log = logging.getLogger()
    log.info("Cleaning")
    raise NotImplementedError("Clean not implemented")


def main():
    """Main"""
    # Strating logs
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")
    file_handler = RotatingFileHandler("simplenet.log", "a", 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    # Parsing args
    args = docopt.docopt(__doc__)
    log.debug(args)

    if args['switch']:
        if args['--with-ip']:
            raise NotImplementedError("--with-ip not available yet")
        switch(args['--name'], args['<interface>'])

    if args['nat']:
        nat()

    if args['clean']:
        clean()

if __name__ == "__main__":
    main()
