""" CLI entry point.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click

from .cli_helper import echo_wrapper, show_version


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--option", default=42, show_default=True, type=int, help="A sample option."
)
@click.option(
    "--dry-run",
    "-D",
    is_flag=True,
    help="Show the intended operations but do not run them (implies --verbose).",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase the verbosity of status messages: use once for normal output, twice "
    "for additional output, and thrice for debug-level output.",
)
@click.argument("ARGUMENT", nargs=-1, type=click.File("r"))
@click.option(
    "--version",
    "-V",
    is_flag=True,
    callback=show_version,
    expose_value=False,
    is_eager=True,
    help="Show the version number and exit.",
)
def main(**kwargs):
    """ Main help topic.
    """
    is_dry_run = kwargs["dry_run"]

    # --dry-run implies at least one --verbose.
    verbose = max(kwargs["verbose"], 1 if is_dry_run else 0)

    # Take echo() for a spin.
    _ = echo_wrapper(verbose)
