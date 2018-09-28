"""
Plugin that spins up a nat.
"""
import plugin
from tools import unix_command


class SimplenetPlugin(plugin.SimplenetPlugin):
    """
    NAT a bridge on a destination interface.

    Usage:
      nat <bridge> <destination>
      nat -h | --help

    Arguments:
        bridge        Bridge to operate on
        destination   Interface where we'll NAT behind
    """

    def __init__(self, command_args):
        self.name = __name__.split(".")[1]
        super(SimplenetPlugin, self).__init__(command_args)
        self.bridge = self.args["<bridge>"]
        self.destination = self.args["<destination>"]

    def start(self):
        self.log.info("Plugin %s started", __name__)
        self.create_nat()

    def clean(self):
        raise NotImplementedError

    def create_nat(self):
        """ Setup a NAT"""
        self.log.info("Creating Nat")
        # Enable ip forwarding
        unix_command("echo 1 > /proc/sys/net/ipv4/ip_forward")
        unix_command("iptables -t nat -A POSTROUTING -o %s -j MASQUERADE" % self.destination)
        unix_command("iptables -A FORWARD -i %s -j ACCEPT" % self.bridge)
        unix_command("iptables -A FORWARD -i %s -j ACCEPT" % self.destination)

    def build(self):
        pass
