# cookiecutter-cli-mit-fixins Makefile for various and sundry project tasks.

# This file is part of cookiecutter-cli-mit-fixins. Copyright 2019 Dave Rogers
# <thedude@yukondude.com>. Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

.SILENT: test


test:
	coverage run --module py.test
	coverage report --fail-under 80 --show-missing --omit='*site-packages*,*__init__.py'
