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
DEFAULT_CONFIG_FILE_OPTION = "config_file"
DEFAULT_PRINT_CONFIG_OPTION = "print_config"


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


def config_command_class(config_file_option=DEFAULT_CONFIG_FILE_OPTION):
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
            config_path = ctx.params[config_file_option]

            if not config_path:
                config_path = DEFAULT_CONFIG_FILE_PATH

            if pathlib.Path(config_path).exists():
                settings = {}

                with open(config_path, "r") as config_file:
                    try:
                        settings = toml.load(config_file)[COMMAND_NAME]
                    except toml.TomlDecodeError as exc:
                        raise CliException(
                            f"Unable to parse configuration file '{config_path}': "
                            f"{exc}"
                        )

                short_switch_list = []

                # Gather all possible "short" switches to help (re)parse the command
                # line below.
                for option in ctx.command.params:
                    if isinstance(option, click.core.Option):
                        for switch in option.opts + option.secondary_opts:
                            if switch.startswith("-") and len(switch) == 2:
                                short_switch_list.append(switch[1])

                short_switches = "".join(short_switch_list)

                for option in ctx.command.params:
                    if option.name not in ctx.params or not isinstance(
                        option, click.core.Option
                    ):
                        continue

                    # Third preferential choice for option value is the declared
                    # default. Second choice is the configuration file setting.
                    value = settings.get(option.name, option.default)

                    # ...and first choice is the value passed on the command line.
                    # Have to check this manually because the context already
                    # includes the default if the option wasn't specified. Click
                    # doesn't seem to report if a value arrived via the default or
                    # explicitly on the command line and I haven't figured a way to
                    # intercept the normal parsing to implement this myself.
                    if is_option_switch_in_arguments(
                        option.opts + option.secondary_opts,
                        short_switches,
                        sys.argv[1:],
                    ):
                        value = ctx.params[option.name]

                    ctx.params[option.name] = value

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
    print_option=DEFAULT_PRINT_CONFIG_OPTION,
    config_file_option=DEFAULT_CONFIG_FILE_OPTION,
    excluded_options=None,
):
    """ Print a sample configuration file that corresponds to the current options and
        exit.
    """
    ctx = click.get_current_context()

    if not ctx.params[print_option]:
        return

    excluded_options = excluded_options if excluded_options is not None else []
    excluded_options.extend((print_option, config_file_option))

    config = print_config(
        options=ctx.command.params,
        excluded_options=excluded_options,
        arguments=ctx.params,
        render_func=render_toml_config,
    )
    echo_wrapper(3)(config)
    ctx.exit()


def is_option_switch_in_arguments(switches, short_switches, arguments):
    """ Return True if the given option switches appear on the command line. This is,
        admittedly, a bit of a hackish re-implementation of the Click argument parser.
    """
    for argument in [a for a in arguments if a.startswith("-")]:
        for switch in switches:
            if argument.startswith(switch):
                # Long switches
                return True

            if len(switch) == 2 and len(argument) >= 2 and argument[1] != "-":
                # Short switches
                for char in argument[1:]:
                    if char not in short_switches:
                        # Hit a character that's not one of the recognized short
                        # switches so it must be part of an argument value.
                        break

                    if char == switch[1]:
                        return True

    return False


def print_config(options, excluded_options, arguments, render_func):
    """ Return the sample configuration file for the defined options and command line
        arguments via the given render function as a string.
    """
    settings = {}

    for option in options:
        if (
            isinstance(option, click.core.Option)
            and not option.is_eager
            and option.name not in excluded_options
        ):
            settings[option.name] = option

    return render_func(settings, arguments)


def render_toml_config(settings, arguments):
    """ Return the settings rendered into a TOML-format configuration file string.
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
