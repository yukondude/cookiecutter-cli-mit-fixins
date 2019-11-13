# cookiecutter-cli-mit-fixins
A [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) template for generating
[Click](https://click.palletsprojects.com/)-based Python command line interfaces with
features up the wazoo.

Copyright 2019 Dave Rogers <thedude@yukondude.com>.  
Licensed under the GNU General Public License, version 3.  
Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

## Installation

When naming your command, choose an all-lowercase name without spaces or hyphens.
Underscores are allowed by aren't particularly desirable.

1. Install Python 3.7, or better: `brew install python` (macOS) or
[just download it](https://www.python.org/downloads/).
1. [Install cookiecutter]():
`brew install cookiecutter` (macOS) or `pip install cookiecutter` (other)
1. [Install Poetry](https://poetry.eustace.io/docs/#installation):
`curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python`
1. Create a virtual environment for your command-line project
(I recommend [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)):
`mkvirtualenv -p $(which python3) <command-name>`
1. From within the virtual environment, generate the project:
`cookiecutter gh:yukondude/cookiecutter-cli-mit-fixins`
1. Enter the project directory and complete the installation:
`cd <command-name> ; make install`
1. Test the initial command line program: ` make test`
1. View the initial command line help text: `<command-name> --help`
1. Try running the command with its sample options and arguments:
`<command-name> -v Makefile .`
(`-v` is to see some output, `Makefile` is an existing file, and `.` is an existing
path--the latter two are required by the sample arguments)
1. Try running the command with the `--print-config` option to print a sample
[TOML](https://github.com/toml-lang/toml)-format configuration file:
`<command-name> --print-config Makefile .`
1. Begin programming your command by first editing the command line interface in the
file `<command-name>/<command-name>/cli.py`.
