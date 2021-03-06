""" CLI entry point.
"""

# This file is part of {{cookiecutter.command_name}}.
# Copyright {{cookiecutter.copyright_year}} {{cookiecutter.author_name}} <{{cookiecutter.author_email}}>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import click

from .cli_helper import (
    cli_config_file_option,
    cli_dry_run_option,
    cli_print_config_option,
    cli_verbose_option,
    cli_version_option,
    config_command_class,
    echo_wrapper,
    handle_print_config_option,
)


@click.command(
    cls=config_command_class(),
    context_settings=dict(help_option_names=["-h", "--help"]),
)
# Sample options.
@click.option("--bool-flag/--no-bool-flag", help="A sample Boolean flag option.")
@click.option(
    "--choice",
    "-c",
    type=click.Choice(("ALP", "BET", "GAM")),
    help="A sample choice option.",
)
@click.option("--feature-a", "feature", flag_value="a", help="A sample feature option.")
@click.option("--feature-b", "feature", flag_value="b", help="A sample feature option.")
@click.option("--flag", "-f", is_flag=True, help="A sample flag.")
@click.option(
    "--multiple", "-m", multiple=True, type=str, help="A sample multiple option."
)
@click.option(
    "--multivalue", "-M", nargs=3, type=float, help="A sample multivalue (3) option."
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
@cli_config_file_option
@cli_dry_run_option
@cli_print_config_option
@cli_verbose_option
@cli_version_option
# Sample arguments.
@click.argument("FILE", type=click.File("r"))
@click.argument("PATH", type=click.Path(exists=True))
@click.argument("STUFF", nargs=-1)
def main(**kwargs):
    """ Main help topic.
    """
    handle_print_config_option()

    is_dry_run = kwargs["dry_run"]

    # --dry-run implies at least one --verbose.
    verbose = max(kwargs["verbose"], 1 if is_dry_run else 0)

    # Take echo() for a spin.
    echo_wrapper(verbose)(kwargs)
