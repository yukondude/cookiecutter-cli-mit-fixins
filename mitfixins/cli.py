""" Console script entry point.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os
import pkg_resources

import click


# The name of this command is its package name.
COMMAND_NAME = os.path.splitext(__name__)[0]

# What to display if the command is not registered (via `poetry install`).
UNREGISTERED_MESSAGE = f"({COMMAND_NAME} is not registered)"


def show_version(ctx, param, value):
    """ Display the version message.
    """
    _ = param

    if not value or ctx.resilient_parsing:
        return  # pragma: no cover

    try:
        version = pkg_resources.get_distribution(COMMAND_NAME).version
    except pkg_resources.DistributionNotFound:
        version = UNREGISTERED_MESSAGE

    click.echo(f"{COMMAND_NAME} version {version}")
    click.echo("Copyright 2019 Dave Rogers. Licensed under the GPLv3. See LICENSE.")
    ctx.exit()


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
@click.argument("ARGUMENT", nargs=-1)
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
    _ = kwargs
