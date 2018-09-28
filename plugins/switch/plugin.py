"""
Plugin that spins up a virtual switch and bridges interfaces.
"""
import ipaddress as ipa

import plugin
from tools import unix_command


class SimplenetPlugin(plugin.SimplenetPlugin):
    """
    Spins up a virtual switch bridging interfaces.
    The switch can be used 

    Usage:
      switch [--bridge NAME] <interface>...
      switch [--bridge NAME] --with-ip [(--ip IP --subnet SUBNET | --dhcp)] <interface>...
      switch -h | --help

    Options:
        -d, --dhcp                        Get ip and subnet by dhcp
        -r, --resolvers DNS               IP of a Domain Name Server [default: 1.1.1.1]
        -h, --help                        Print this help and exit.
        -i, --ip IP                       Machine ip on the bridge [default: 192.168.2.2]
        -s, --bridge NAME                 Name of the switch/bridge [default: br0]
            --subnet SUBNET               Subnet of the bridge [default: 192.168.2.0/24]
        -w, --with-ip                     Connect the current machine to the virtual switch

    Arguments:
        interface       Interface you want to add
    """

    def __init__(self, command_args):
        self.name = __name__.split(".")[1]
        super(SimplenetPlugin, self).__init__(command_args)
        self.switch = self.args["--bridge"]
        self.interfaces = self.args["<interface>"]
        self.with_ip = self.args["--with-ip"]
        self.dhcp = self.args["--dhcp"]
        self.ip_address = ipa.ip_address(self.args["--ip"])
        self.subnet = ipa.ip_network(self.args["--subnet"])

    def start(self):
        self.log.info("Plugin %s started", __name__)
        self.create_switch()

    def clean(self):
        self.log.info("Deleting route %s", self.subnet)
        unix_command("ip route del %s" % self.subnet, fatal=False)
        self.log.info("Setting down switch %s", self.switch)
        unix_command("ip link set %s down" % self.switch, fatal=False)
        self.log.info("Cleaning switch %s", self.switch)
        unix_command("brctl delbr %s" % self.switch, fatal=False)

    def create_switch(self):
        """ Setup a virtual switch on given ports.
        Can get tha machine an IP and setup a DHCP server
        """
        self.log.info("Creating switch %s", self.switch)
        unix_command("brctl addbr %s" % self.switch)
        # set forward delay to 0
        unix_command("brctl setfd %s 0" % self.switch)
        # we add each interface to the bridge
        for interface in self.interfaces:
            self.log.info("Adding interface %s to bridge %s", interface, self.switch)
            unix_command("brctl addif %s %s" % (self.switch, interface))
        self.log.info("Setting switch %s up", self.switch)
        unix_command("ip link set %s up" % self.switch)
        # Let's get an IP address if needed
        if self.with_ip:
            if self.dhcp:
                self.log.info("Acquiring an ip with dhcp")
                unix_command("dhclient -v %s" % self.switch)
            else:
                self.log.info(
                    "Setting ip address %s/%d on bridge %s",
                    self.ip_address,
                    self.subnet.prefixlen,
                    self.switch,
                )
                unix_command(
                    "ip a add %s/%d dev %s"
                    % (self.ip_address, self.subnet.prefixlen, self.switch)
                )
                self.log.info("Setting up route via bridge %s", self.switch)
                unix_command(
                    "ip route add %s dev %s" % (self.subnet, self.switch), fatal=False
                )

    def build(self):
        pass
