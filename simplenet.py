#!/usr/bin/env python3

"""
Spins up a virtual switch to bridge network interfaces.
Can setup a dhcp server and a nat.

Usage:
  simplenet switch [--name NAME] <interface>...
  simplenet switch [--name NAME] --with-ip [(--ip IP --subnet SUBNET | --dhcp)] <interface>...
  simplenet nat <bridge> <destination>
  simplenet clean [--name NAME] [--subnet SUBNET] [--except=<exception>]...
  simplenet dhcp [--subnet SUBNET] [--gateway GATEWAY] [--dns DNS]...
  simplenet radius [--secret SECRET] [--credentials CREDENTIALS]
  simplenet -h | --help
  simplenet --version

Options:
    -d, --dhcp                        Get ip and subnet by dhcp
    -r, --resolvers DNS               IP of a Domain Name Server [default: 1.1.1.1]
    -e, --except <exception>...       Do not touch this interface while cleaning
    -h, --help                        Print this help and exit.
    -i, --ip IP                       Machine ip on the bridge [default: 192.168.2.2]
    -g, --gateway GATEWAY             Gateway IP [default: 192.168.2.2]
    -n, --name NAME                   Name of the bridge [default: br0]
    -s, --subnet SUBNET               Subnet of the bridge [default: 192.168.2.0/24]
        --secret SECRET               Radius secret (for clients) [default: simplesecret]
    -w, --with-ip                     Connect the current machine to the virtual switch

Arguments:
    interface     Interface you want to add
    bridge        Bridge to operate on
    destination   Interface where we'll NAT behind
"""


import logging
import subprocess
import ipaddress as ipa

# import jinja2 as j2
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


def switch(name, interfaces, with_ip, with_dhcp, ip_address, subnet):
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
    log.info("Setting switch %s up", name)
    unix_command("ip link set %s up" % name)
    if with_ip:
        if with_dhcp:
            log.info("Acquiring an ip with dhcp")
            unix_command("dhclient -v %s" %name)
        else:
            log.info(
                "Setting ip address %s/%d on bridge %s",
                ip_address,
                subnet.prefixlen,
                name,
            )
            unix_command("ip a add %s/%d dev %s" % (ip_address, subnet.prefixlen, name))
            log.info("Setting up route via bridge %s", name)
            unix_command("ip route add %s dev %s" % (subnet, name), fatal=False)


def nat(bridge, destination):
    """Sets up a NAT"""
    log = logging.getLogger()
    log.info("Creating Nat")
    unix_command("echo 1 > /proc/sys/net/ipv4/ip_forward")
    unix_command("iptables -t nat -A POSTROUTING -o %s -j MASQUERADE" % destination)
    unix_command("iptables -A FORWARD -i %s -j ACCEPT" % bridge)
    unix_command("iptables -A FORWARD -i %s -j ACCEPT" % destination)


def dhcp(bridge, subnet, gateway, dns):
    """Sets up a DHCP server on a given bridge for a given ip range"""
    log = logging.getLogger()
    raise NotImplementedError()
    log.info("Creating DHCP server")


def clean(name, subnet):
    """Clean our shit"""
    log = logging.getLogger()
    log.info("Deleting route %s", subnet)
    unix_command("ip route del %s" % subnet, fatal=False)
    log.info("Setting down switch %s", name)
    unix_command("ip link set %s down" % name, fatal=False)
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
        clean(args["--name"], args["--subnet"])

    elif args["switch"]:
        switch(
            args["--name"],
            args["<interface>"],
            args["--with-ip"],
            args["--dhcp"],
            ipa.ip_address(args["--ip"]),
            ipa.ip_network(args["--subnet"]),
        )

    elif args["nat"]:
        nat(args["<bridge>"], args["<destination>"])

    elif args["dhcp"]:
        dhcp(args["<bridge>"], args["--subnet"], args["--gateway"], args["--dns"])


if __name__ == "__main__":
    main()
