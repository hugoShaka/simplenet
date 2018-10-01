"""Tools shared by simplenet plugins"""
import logging
import subprocess


def unix_command(command, *, log=logging.getLogger(__name__), fatal=True):
    """Takes a string representing the command, executes the command"""
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
