""" Shared unit test code.
"""

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

import configparser
import os

import pytest


@pytest.fixture(scope="session")
def version_message():
    pyproject = configparser.ConfigParser()
    pyproject.read(os.path.join(os.path.splitext(__name__)[0], "..", "pyproject.toml"))
    command_name = pyproject["tool.poetry"]["name"].strip('"')
    version = pyproject["tool.poetry"]["version"].strip('"')
    copyright_msg = "Copyright 2019 Dave Rogers. Licensed under the GPLv3. See LICENSE."
    return f"{command_name} version {version}\n{copyright_msg}\n"
