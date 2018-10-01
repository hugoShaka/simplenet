#!/usr/bin/env python3

"""
Spins up a virtual switch to bridge network interfaces.
Can setup a dhcp server and a nat.

Usage:
  simplenet clean [--bridge NAME] [--subnet SUBNET]
  simplenet <command> [<args>...]
  simplenet -h | --help
  simplenet --version

Options:
    -e, --except <exception>...       Do not touch this interface while cleaning
    -h, --help                        Print this help and exit.
    -n, --name NAME                   Name of the bridge [default: br0]
    -s, --subnet SUBNET               Subnet of the bridge [default: 192.168.2.0/24]

The plugins are:
    dhcp          Spins up a kea dhcp server
    switch        Bridges interfaces together with a virtual switch
    nat           Nat a bridge behind an interface
    radius        Spins up a radius server
"""


import logging

import docopt

from tools import unix_command


def clean(args):
    """Clean our mess"""
    raise NotImplementedError


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
    # option_first makes docopts happy
    args = docopt.docopt(__doc__, options_first=True)
    log.debug(args)
    if args["clean"]:
        clean(args)
    else:
        plugin_name = args.pop("<command>")
        plugin_args = args.pop("<args>")
        log.debug("Plugin %s called with args %s", plugin_name, plugin_args)
        if plugin_args is None:
            plugin_args = {}
        try:
            log.info("Importing module %s", plugin_name)
            module = __import__("plugins.%s.plugin" % plugin_name)
            plugin_module = getattr(module, plugin_name)

        except (ModuleNotFoundError) as err:
            log.error(err)
            raise docopt.DocoptExit()

        plugin = plugin_module.plugin.SimplenetPlugin(plugin_args)
        plugin.start()

#    if args["clean"]:
#        clean(args["--name"], args["--subnet"])
#
#    elif args["switch"]:
#        switch(
#            args["--name"],
#            args["<interface>"],
#            args["--with-ip"],
#            args["--dhcp"],
#            ipa.ip_address(args["--ip"]),
#            ipa.ip_network(args["--subnet"]),
#        )
#
#    elif args["nat"]:
#        nat(args["<bridge>"], args["<destination>"])
#
#    elif args["dhcp"]:
#

if __name__ == "__main__":
    main()
