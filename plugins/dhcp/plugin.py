"""
Plugin that spins up a kea dhcp server.
"""
import ipaddress as ipa

import docker
import jinja2 as j2

import plugin
from tools import unix_command


class SimplenetPlugin(plugin.SimplenetPlugin):
    """
    Spins up a kea dhcp server on a bridge.

    Usage:
      dhcp <bridge> [--subnet SUBNET] [--gateway GATEWAY] [--resolvers DNS]...
      dhcp -h | --help

    Options:
        -r, --resolvers DNS               IP of a Domain Name Server [default: 1.1.1.1]
        -h, --help                        Print this help and exit.
        -g, --gateway GATEWAY             Gateway IP [default: 192.168.2.2]
        -s, --subnet SUBNET               Subnet of the bridge [default: 192.168.2.0/24]

    Arguments:
        bridge        Bridge to operate on
    """

    def __init__(self, command_args):
        self.name = __name__.split(".")[1]
        super(SimplenetPlugin, self).__init__(command_args)
        self.client = docker.from_env()
        self.bridge = self.args["<bridge>"]
        self.subnet = ipa.ip_network(self.args["--subnet"])
        self.gateway = ipa.ip_address(self.args["--gateway"])
        self.dns = self.args["--resolvers"]

    def start(self):
        self.log.info("Plugin %s started", __name__)
        self.generate_conf()
        self.run_container()

    def clean(self):
        self.log.info("Cleaning dhcp container")
        unix_command("docker rm -f simplenet-dhcp", fatal=False)

    def generate_conf(self):
        """Generates the kea conf file with jinja2 in .tmp"""

        # is the range too small ?
        assert self.subnet.num_addresses >= 4

        self.log.info("Generating dhcp configuration with jinja2")
        j2_env = j2.Environment(
            loader=j2.FileSystemLoader(self.plugin_dir), trim_blocks=True
        )

        conf = j2_env.get_template("kea-dhcp4.conf.j2").render(
            bridge=self.bridge,
            subnet=self.subnet,
            range_start=self.subnet.network_address + 2,
            range_end=self.subnet.network_address + self.subnet.num_addresses - 2,
            gateway=self.gateway,
            dns=",".join(self.dns),
        )
        with open("%s/kea-dhcp4.conf" % self.temp_dir, "w") as conf_file:
            conf_file.write(conf)

    def run_container(self):
        """Starts the kea container"""
        self.log.info("Creating DHCP server on bridge %s", self.bridge)

        self.client.containers.run(
            "simplenet-dhcp",
            name="simplenet-dhcp",
            command=["-c", "/etc/kea/kea-dhcp4.conf"],
            detach=True,
            ports={"67/udp": 67},
            network_mode="host",
            cap_add=["NET_ADMIN"],
            volumes={
                "%s/kea-dhcp4.conf"
                % self.temp_dir: {"bind": "/etc/kea/kea-dhcp4.conf", "mode": "ro"}
            },
        )

    def build(self):
        pass
