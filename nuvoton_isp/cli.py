# -*- coding: utf-8 -*-

"""Console script for nuvoton_isp."""
import sys

import click

from nuvoton_isp.isp import Usb


@click.command()
@click.option('--firmware', '-f', required=True, help="Firmware bin file")
def main(firmware):
    """Console script for nuvoton_isp."""
    isp = Usb()
    isp.link_fun()
    isp.sn_fun()
    isp.read_pid_fun()
    isp.read_fw_fun()
    isp.read_aprom_bin_file(firmware)
    isp.update_aprom()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
