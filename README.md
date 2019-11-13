# cookiecutter-cli-mit-fixins
A [cookiecutter](https://cookiecutter.readthedocs.io/en/latest/) template for generating
[Click](https://click.palletsprojects.com/)-based Python command line interfaces with
features up the wazoo.

## Installation

This isn't fully figured out yet, but here's the gist.
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
1. Begin programming your command by first editing the command line interface in the
file `<command-name>/<command-name>/cli.py`.
