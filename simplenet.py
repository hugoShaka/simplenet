#!/usr/bin/env python3

"""
Spins up a virtual switch to bridge eth ports.
Can setup a dhcp server and a nat.

Usage:
  simplenet switch [--name NAME] <interface>...
  simplenet switch [--name NAME] --with-ip [(--ip IP --subnet SUBNET | --dhcp)] <interface>...
  simplenet nat <bridge> <destination>
  simplenet clean [--name NAME] [--except=<exception>]...
  simplenet -h | --help
  simplenet --version

Options:
    -d, --dhcp                        Get ip and subnet by dhcp
    -e, --except <exception>...       Do not touch this interface
    -h, --help                        Print this help and exit.
    -i, --ip IP                       Machine ip on the bridge [default: 192.168.2.2]
    -n, --name NAME                   Name of the bridge [default: br0]
    -s, --subnet SUBNET               Subnet of the bridge [default: 192.168.2.0/24]
    -w, --with-ip                     Connect the current machine to the bridged network

Arguments:
    interface     Interface you want to add
    bridge        Bridge to operate on
    destination   Interface where we'll NAT behind
"""


import logging
import subprocess

import docopt


def unix_command(command, *, fatal=True):
    """Takes a string representing the command, executes the command"""
    log = logging.getLogger()
    try:
        _ = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            shell=True,
            timeout=3,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as exc:
        log.error(
            """Command "%s" returned %d :
               stdout: %r""",
            command,
            exc.returncode,
            exc.output,
        )
        if fatal:
            log.critical("Stopping program because a command failed")
            raise


def checks():
    """ Do the checks :
    - is bridge-utils available
    - are we root
    - do we have IPs """
    log = logging.getLogger()
    log.info("Running checks")


def switch(name, interfaces, with_ip=False, dhcp=False, ip=None, subnet=None):
    """ Setup a virtual switch on given ports.
    Can get tha machine an IP and setup a DHCP server
    """
    log = logging.getLogger()
    log.info("Creating switch %s", name)
    unix_command("brctl addbr %s" % name)
    unix_command("brctl setfd %s 0" % name)
    for interface in interfaces:
        log.info("Adding interface %s to bridge %s", interface, name)
        unix_command("brctl addif %s %s" % (name, interface))


def nat():
    """Sets up a NAT"""
    log = logging.getLogger()
    log.info("Creating Nat")
    raise NotImplementedError("Nat not implemented")
    # echo 1 > /proc/sys/net/ipv4/ip_forward
    # iptables -t nat -A POSTROUTING -o destination -j MASQUERADE
    # iptables -A FORWARD -i brname -j ACCEPT


def dhcp():
    """Sets up a DHCP server on a given bridge for a given ip range"""
    log = logging.getLogger()
    log.info("Creating DHCP server")


def clean(name):
    """Clean our shit"""
    log = logging.getLogger()
    log.info("Cleaning switch %s", name)
    unix_command("brctl delbr %s" % name, fatal=False)


def main():
    """Main"""
    # Strating logs
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s")
    file_handler = logging.FileHandler("simplenet.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    # Parsing args
    args = docopt.docopt(__doc__)
    log.debug(args)

    if args["clean"]:
        clean(args["--name"])

    elif args["switch"]:
        if args["--with-ip"]:
            raise NotImplementedError("--with-ip not available yet")
        switch(
            args["--name"],
            args["<interface>"],
            args["--with-ip"],
            args["--dhcp"],
            args["--ip"],
            args["--subnet"],
        )

    if args["nat"]:
        nat()


if __name__ == "__main__":
    main()
