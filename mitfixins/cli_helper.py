""" CLI helper functions.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os
import pathlib
import sys

import pkg_resources

import click
import toml

# noinspection PyProtectedMember
from click._compat import get_text_stderr
from click.utils import echo as click_utils_echo


COMMAND_NAME = os.path.splitext(__name__)[0]
DEFAULT_CONFIG_FILE_PATH = os.path.join(
    click.get_app_dir(app_name=COMMAND_NAME, force_posix=True), f"{COMMAND_NAME}.toml"
)
CONFIG_FILE_OPTION = "config_file"


def cli_config_file_option(func):
    """ Decorator to enable the --config-file/-C option.
    """
    return click.option(
        "--config-file",
        "-C",
        type=click.Path(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
        help="Full path of the TOML-format configuration file.",
    )(func)


def cli_dry_run_option(func):
    """ Decorator to enable the --dry-run/-D option.
    """
    return click.option(
        "--dry-run",
        "-D",
        is_flag=True,
        help="Show the intended operations but do not run them (implies --verbose).",
    )(func)


def cli_print_config_option(func):
    """ Decorator to enable the --print-config option.
    """
    return click.option(
        "--print-config",
        is_flag=True,
        help="Print a sample configuration file that corresponds to the command "
        "line options and exit. Ignores the settings from a configuration file.",
    )(func)


def cli_verbose_option(func):
    """ Decorator to enable the --verbose/-v option.
    """
    return click.option(
        "--verbose",
        "-v",
        count=True,
        help="Increase the verbosity of status messages: use once for normal output, "
        "twice for additional output, and thrice for debug-level output.",
    )(func)


def cli_version_option(func):
    """ Decorator to enable the --version/-V option.
    """
    return click.option(
        "--version",
        "-V",
        is_flag=True,
        callback=show_version,
        expose_value=False,
        is_eager=True,
        help="Show the version number and exit.",
    )(func)


class CliException(click.ClickException):
    """ ClickException overridden to display errors using echo_wrapper()'s formatting.
    """

    def show(self, file=None):
        """ Display the error.
        """
        _ = file
        echo_wrapper(0)(self.format_message(), severity=3)


def config_command_class(path_option=CONFIG_FILE_OPTION):
    """ Return a custom Command class that loads any configuration file before
        arguments passed on the command line.
        Based on https://stackoverflow.com/a/46391887/726
    """

    class ConfigCommand(click.Command):
        """ Click Command subclass that loads settings from a configuration file.
        """

        def invoke(self, ctx):
            """ Load the configuration settings into the context.
            """
            config_path = ctx.params[path_option]

            if not config_path:
                config_path = DEFAULT_CONFIG_FILE_PATH

            if pathlib.Path(config_path).exists():
                with open(config_path, "r") as config_file:
                    try:
                        settings = toml.load(config_file)[COMMAND_NAME]
                    except toml.TomlDecodeError as exc:
                        raise CliException(
                            f"Unable to parse configuration file '{config_path}': "
                            f"{exc}"
                        )

                    # TODO: have to interpret in order: default, config, command
                    for param, value in ctx.params.items():
                        if value is None and param in settings:
                            ctx.params[param] = settings[param]

            return super().invoke(ctx)

    return ConfigCommand


def echo_wrapper(verbosity):
    """ Return an echo function that displays or doesn't based on the verbosity count.
    """
    severity_ranks = {
        1: {"prefix": "", "style": {"fg": "green", "bold": False}},
        2: {"prefix": "WARNING ", "style": {"fg": "yellow", "bold": True}},
        3: {"prefix": "ERROR ", "style": {"fg": "red", "bold": True}},
    }

    # Clamp the verbosity between 0 and 3.
    verbosity = min(max(verbosity, 0), 3)

    def echo_func(message, threshold=1, severity=1):
        """ Display the message if the given threshold is no greater than the current
            verbosity count. Errors are always displayed. Warnings are displayed if the
            verbosity count is at least 1. Errors and warnings are sent to STDERR.
        """
        # Clamp the threshold and severity between 1 and 3.
        threshold = min(max(threshold, 1), 3)
        severity = min(max(severity, 1), 3)

        if severity == 2:
            # Display warnings if verbosity is turned on at all.
            threshold = 1
        elif severity >= 3:
            # Always display errors.
            threshold = 0

        if threshold <= verbosity:
            severity_rank = severity_ranks.get(severity, severity_ranks[3])
            prefix = severity_rank["prefix"]
            style = severity_rank["style"]

            is_err = severity > 1
            click.secho(f"{prefix}{message}", err=is_err, **style)

    return echo_func


def handle_print_config_option(
    print_option="print_config",
    config_file_option=CONFIG_FILE_OPTION,
    excluded_options=None,
):
    """ Print a sample configuration file that corresponds to the current options and
        exit.
    """

    def render_toml(settings, arguments):
        """ Render settings into a TOML-format configuration file string.
        """
        lines = [
            f"# Sample {COMMAND_NAME} configuration file, by default located at "
            f"{DEFAULT_CONFIG_FILE_PATH}.",
            "# Configuration options already set to the default value are "
            "commented-out.",
            "",
            f"[{COMMAND_NAME}]",
            "",
        ]

        for setting_name in sorted(settings):
            setting = settings[setting_name]
            argument = arguments[setting_name]

            if argument is not None and argument != ():
                lines.append(f"# {setting.help}")
                prefix = "# " if argument == setting.default else ""
                toml_setting = toml.dumps({setting_name: argument})
                lines.append(f"{prefix}{toml_setting}")

        return "\n".join(lines).strip()

    ctx = click.get_current_context()

    if not ctx.params[print_option]:
        return

    excluded_options = excluded_options if excluded_options is not None else []
    excluded_options.extend((print_option, config_file_option))
    options = {}

    for option in ctx.command.params:
        if (
            isinstance(option, click.core.Option)
            and not option.is_eager
            and option.name not in excluded_options
        ):
            options[option.name] = option

    echo_wrapper(3)(render_toml(settings=options, arguments=ctx.params))
    ctx.exit()


def _show_usage(self, file=None):
    """ Override the standard usage error message with a splash of colour.
        Taken from https://stackoverflow.com/a/43922088/726
    """
    if file is None:
        file = get_text_stderr()

    if self.ctx is not None:
        color = self.ctx.color
        click_utils_echo(self.ctx.get_usage() + "\n", file=file, color=color)

    echo_wrapper(0)(self.format_message(), severity=3)
    sys.exit(1)


# Replace the usage error display function with show_usage().
click.exceptions.UsageError.show = _show_usage


def show_version(ctx, param, value):
    """ Show the version number and exit.
    """
    _ = param

    if not value or ctx.resilient_parsing:
        return

    try:
        version = pkg_resources.get_distribution(COMMAND_NAME).version
    except pkg_resources.DistributionNotFound:  # pragma: no cover
        version = f"({COMMAND_NAME} is not registered)"

    click.echo(f"{COMMAND_NAME} version {version}")
    click.echo("Copyright 2019 Dave Rogers. Licensed under the GPLv3. See LICENSE.")
    ctx.exit()
