# -*- coding: utf-8 -*-

"""Console script for nuvoton_isp."""
import sys
import click


@click.command()
@click.option('--firmware', '-f', help="Firmware bin file")
def main(firmware):
    """Console script for nuvoton_isp."""
    click.echo("See click documentation at http://click.pocoo.org/")


    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
