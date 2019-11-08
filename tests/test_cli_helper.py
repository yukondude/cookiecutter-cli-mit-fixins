""" Console script entry point unit tests.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import configparser
import os

import pytest

from mitfixins.cli_helper import echo_wrapper, show_version


@pytest.mark.parametrize("arguments,expected", [
    # verbosity, threshold, severity, message:   stdout,  stderr
    ((-1,        1,         1,        "info"),  ("",      "")),
    ((0,         1,         0,        "info"),  ("",      "")),
    ((0,         1,         1,        "info"),  ("",      "")),
    ((1,         1,         1,        "info"),  ("info",  "")),
    ((2,         1,         1,        "info"),  ("info",  "")),
    ((3,         1,         1,        "info"),  ("info",  "")),
    ((4,         1,         1,        "info"),  ("info",  "")),
    ((0,         1,         2,        "warn"),  ("",      "")),
    ((1,         1,         2,        "warn"),  ("",      "WARNING warn")),
    ((2,         1,         2,        "warn"),  ("",      "WARNING warn")),
    ((3,         1,         2,        "warn"),  ("",      "WARNING warn")),
    ((0,         1,         3,        "error"), ("",      "ERROR error")),
    ((1,         1,         3,        "error"), ("",      "ERROR error")),
    ((2,         1,         3,        "error"), ("",      "ERROR error")),
    ((3,         1,         3,        "error"), ("",      "ERROR error")),
    ((3,         1,         4,        "error"), ("",      "ERROR error")),
    ((0,         0,         1,        "info"),  ("",      "")),
    ((0,         1,         1,        "info"),  ("",      "")),
    ((0,         2,         1,        "more"),  ("",      "")),
    ((0,         3,         1,        "debug"), ("",      "")),
    ((0,         4,         1,        "debug"), ("",      "")),
    ((1,         0,         1,        "info"),  ("info",  "")),
    ((1,         1,         1,        "info"),  ("info",  "")),
    ((1,         2,         1,        "more"),  ("",      "")),
    ((1,         3,         1,        "debug"), ("",      "")),
    ((1,         4,         1,        "debug"), ("",      "")),
    ((2,         0,         1,        "info"),  ("info",  "")),
    ((2,         1,         1,        "info"),  ("info",  "")),
    ((2,         2,         1,        "more"),  ("more",  "")),
    ((2,         3,         1,        "debug"), ("",      "")),
    ((2,         4,         1,        "debug"), ("",      "")),
    ((3,         0,         1,        "info"),  ("info",  "")),
    ((3,         1,         1,        "info"),  ("info",  "")),
    ((3,         2,         1,        "more"),  ("more",  "")),
    ((3,         3,         1,        "debug"), ("debug", "")),
    ((3,         4,         1,        "debug"), ("debug", "")),
])
def test_echo_wrapper(capsys, arguments, expected):
    verbosity, threshold, severity, message = arguments
    expected_out, expected_err = expected

    echo = echo_wrapper(verbosity)
    echo(message, threshold, severity)

    captured_out, captured_err = capsys.readouterr()
    assert captured_out.strip() == expected_out
    assert captured_err.strip() == expected_err


def test_show_version_fail(capsys):
    show_version(None, None, None)
    captured_out, captured_err = capsys.readouterr()
    assert captured_out == ""
    assert captured_err == ""


def test_show_version(capsys):
    class MockContext:
        resilient_parsing = False

        def exit(self):
            pass

    show_version(MockContext(), None, True)
    captured_out, captured_err = capsys.readouterr()

    pyproject = configparser.ConfigParser()
    pyproject.read(os.path.join(os.path.splitext(__name__)[0], "..", "pyproject.toml"))
    command_name = pyproject["tool.poetry"]["name"].strip('"')
    version = pyproject["tool.poetry"]["version"].strip('"')
    copyright = "Copyright 2019 Dave Rogers. Licensed under the GPLv3. See LICENSE."

    assert captured_out == f"{command_name} version {version}\n{copyright}\n"
    assert captured_err == ""
