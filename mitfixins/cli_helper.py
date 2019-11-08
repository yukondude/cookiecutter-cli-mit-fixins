""" CLI helper functions.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import os
import sys

import pkg_resources

import click
from click._compat import get_text_stderr
from click.utils import echo


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


def modify_usage_error(main_command):
    """ Override the standard error behaviour with a splash of colour.
        Taken from https://stackoverflow.com/a/43922088/726
    """

    def show(self, file=None):
        if file is None:
            file = get_text_stderr()

        if self.ctx is not None:
            color = self.ctx.color
            echo(self.ctx.get_usage() + "\n", file=file, color=color)

        echo_wrapper(0)(self.format_message(), severity=3)
        sys.argv = [sys.argv[0]]
        main_command()

    click.exceptions.UsageError.show = show


def show_version(ctx, param, value):
    """ Show the version number and exit.
    """
    _ = param

    if not value or ctx.resilient_parsing:
        return

    command_name = os.path.splitext(__name__)[0]

    try:
        version = pkg_resources.get_distribution(command_name).version
    except pkg_resources.DistributionNotFound:  # pragma: no cover
        version = f"({command_name} is not registered)"

    click.echo(f"{command_name} version {version}")
    click.echo("Copyright 2019 Dave Rogers. Licensed under the GPLv3. See LICENSE.")
    ctx.exit()
