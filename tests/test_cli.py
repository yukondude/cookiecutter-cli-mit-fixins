""" CLI entry point unit tests.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

from click.testing import CliRunner
import pytest

from mitfixins.cli import main


@pytest.mark.parametrize("switch", ["-h", "--help"])
def test_cli_help(switch):
    result = CliRunner().invoke(main, [switch])
    assert result.exit_code == 0
    assert result.output.startswith("Usage: ")
    assert result.output.endswith("Show this message and exit.\n")


@pytest.mark.parametrize("switch", ["-V", "--version"])
def test_cli_version(switch, version_message):
    result = CliRunner().invoke(main, [switch])
    assert result.exit_code == 0
    assert result.output == version_message
