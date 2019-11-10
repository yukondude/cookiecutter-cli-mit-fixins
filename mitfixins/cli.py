""" CLI entry point.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click

from .cli_helper import echo_wrapper, print_config, show_version


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
# Sample options.
@click.option("--bool-flag/--no-bool-flag", help="A sample Boolean flag option.")
@click.option(
    "--choice",
    "-c",
    type=click.Choice(("ALP", "BET", "GAM")),
    help="A sample choice option.",
)
@click.option(
    "--feature-a", "feature", flag_value="a", help="A sample feature A option."
)
@click.option(
    "--feature-b",
    "feature",
    default=True,
    flag_value="b",
    show_default=True,
    help="A sample feature B option.",
)
@click.option("--flag", "-f", is_flag=True, help="A sample flag.")
@click.option(
    "--multiple", "-m", multiple=True, type=str, help="A sample multiple option."
)
@click.option(
    "--multivalue", "-M", nargs=3, type=float, help="A sample 3-value option."
)
@click.option(
    "--multivalue-tuple",
    "-T",
    default=(False, "nada", 0),
    show_default=True,
    type=(bool, str, int),
    help="sample 3-value-tuple option.",
)
@click.option(
    "--option", "-o", default=42, show_default=True, type=int, help="A sample option."
)
@click.option(
    "--range",
    "-r",
    type=click.IntRange(0, 10, clamp=True),
    help="A sample integer range option.",
)
@click.option("--secret", hidden=True, help="A sample hidden option.")
# Standard options.
@click.option(
    "--dry-run",
    "-D",
    is_flag=True,
    help="Show the intended operations but do not run them (implies --verbose).",
)
@click.option(
    "--print-config",
    is_flag=True,
    help="Print the configuration file that corresponds to the current options and "
    "exit.",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase the verbosity of status messages: use once for normal output, twice "
    "for additional output, and thrice for debug-level output.",
)
@click.option(
    "--version",
    "-V",
    is_flag=True,
    callback=show_version,
    expose_value=False,
    is_eager=True,
    help="Show the version number and exit.",
)
# Sample argument.
@click.argument("FILE", type=click.File("r"))
@click.argument("PATH", type=click.Path(exists=True))
@click.argument("STUFF", nargs=-1)
def main(**kwargs):
    """ Main help topic.
    """
    if kwargs["print_config"]:
        print_config(kwargs, excludes=["print_config"])

    is_dry_run = kwargs["dry_run"]

    # --dry-run implies at least one --verbose.
    verbose = max(kwargs["verbose"], 1 if is_dry_run else 0)

    # Take echo() for a spin.
    _ = echo_wrapper(verbose)
