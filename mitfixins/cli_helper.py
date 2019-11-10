""" CLI helper functions.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os
import sys

import pkg_resources

import click
import toml

# noinspection PyProtectedMember
from click._compat import get_text_stderr
from click.utils import echo as click_utils_echo


COMMAND_NAME = os.path.splitext(__name__)[0]


class ConfigHelper:
    """ Helper class for configuration file chores.
    """

    def __init__(
        self,
        print_option="print_config",
        path_option="config_path",
        excluded_options=None,
    ):
        """
        :param print_option: The name of the flag option to print the sample config
        file.
        :param path_option: The name of the option for choosing the config file path.
        :param excluded_options: Option names to exclude from all configuration-related
        activities.
        """
        self.excluded_options = excluded_options if excluded_options is not None else []
        self.excluded_options.append(print_option)
        self.excluded_options.append(path_option)
        self.print_option = print_option
        self.path_option = path_option
        self.config_file_path = os.path.join(
            click.get_app_dir(app_name=COMMAND_NAME, force_posix=True),
            f"{COMMAND_NAME}.toml",
        )

    def act(self, arguments):
        """ Evaluate the options passed in the constructor and act accordingly. Changes
            may be made to the mutable arguments dictionary.
        """
        if arguments.get(self.print_option, False):
            self.print(arguments)

        # TODO read from config file and merge into arguments.
        # if self.path_option in arguments:
        #     self.config_path = arguments[self.path_option]
        # self.config_path = click.get_app_dir(app_name=COMMAND_NAME,
        #                                      force_posix=True)

    def print(self, arguments):
        """ Print a sample configuration file that corresponds to the current options
            and exit.
        """

        def render(settings):
            """ Render settings into a TOML-format configuration file string.
            """
            lines = [
                f"# Sample {COMMAND_NAME} configuration file, by default located at "
                f"{self.config_file_path}.",
                "# Configuration options already set to the default value are "
                "commented-out.",
                "",
                f"[{COMMAND_NAME}]",
                "",
            ]

            for setting_name in sorted(settings):
                setting = settings[setting_name]

                if setting.argument is not None and setting.argument != ():
                    lines.append(f"# {setting.help}")
                    prefix = "# " if setting.argument == setting.default else ""
                    toml_setting = toml.dumps({setting_name: setting.argument})
                    lines.append(f"{prefix}{toml_setting}")

            return "\n".join(lines).strip()

        ctx = click.get_current_context()
        options = {}

        for option in ctx.command.params:
            if (
                isinstance(option, click.core.Option)
                and not option.is_eager
                and option.name not in self.excluded_options
            ):
                option.__dict__["argument"] = arguments.get(option.name, option.default)
                options[option.name] = option

        echo_wrapper(3)(render(options))
        ctx.exit()


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


def show_usage(self, file=None):
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
click.exceptions.UsageError.show = show_usage


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
