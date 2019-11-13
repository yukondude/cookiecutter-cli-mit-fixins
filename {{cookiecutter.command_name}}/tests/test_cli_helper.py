""" CLI helper function unit tests.
"""

# This file is part of cookiecutter-cli-mit-fixins.
# Copyright 2019 Dave Rogers <thedude@yukondude.com>.
# Licensed under the GNU General Public License, version 3.
# Refer to the attached LICENSE file or see <http://www.gnu.org/licenses/> for details.

from click.core import Option
from click.testing import CliRunner
import pytest

from {{cookiecutter.command_name}}.cli_helper import (
    CliException,
    COMMAND_NAME,
    DEFAULT_CONFIG_FILE_PATH,
    echo_wrapper,
    get_short_switches,
    is_option_switch_in_arguments,
    load_toml_config,
    print_config,
    render_toml_config,
    show_version,
)


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


@pytest.mark.parametrize("options,expected", [
    # options,                                                expected
    ((Option(["--apple"]),),                                  ""),
    ((Option(["--apple", "-a"]),),                            "a"),
    ((Option(["--apple", "-a"]), Option(["--banana", "-B"])), "aB"),
])
def test_get_short_switches(options, expected):
    assert get_short_switches(options) == expected


@pytest.mark.parametrize("switches,short_switches,arguments,expected", [
    # switches,         short_switches, arguments,                    expected
    (("-a", "--apple"), "aBcD",         ("",),                        False),
    (("-a", "--apple"), "aBcD",         ("--banana",),                False),
    (("-a", "--apple"), "aBcD",         ("-a",),                      True),
    (("-a", "--apple"), "aBcD",         ("--apple",),                 True),
    (("-a", "--apple"), "aBcD",         ("-BcDaqux",),                True),
    (("-a", "--apple"), "aBcD",         ("-BcEaqux",),                False),
    (("-p", "--apple"), "aBcD",         ("apple",),                   False),
    (("-p", "--apple"), "aBcD",         ("-apple",),                  False),
    (("-p", "--apple"), "aBcD",         ("---apple",),                False),
    (("-p", "--apple"), "aBcD",         ("p",),                       False),
    (("-p", "--apple"), "aBcD",         ("--p",),                     False),
    (("-a", "--apple"), "aBcD",         ("-D", "--banana", "-a"),     True),
    (("-a", "--apple"), "aBcD",         ("-D", "--apple", "food"),    True),
    (("-a", "--apple"), "aBcD",         ("-D", "--apple=food", "-a"), True),
])
def test_is_option_switch_in_arguments(switches, short_switches, arguments, expected):
    assert is_option_switch_in_arguments(switches, short_switches, arguments) == \
           expected


def test_load_toml_config_fail():
    with CliRunner().isolated_filesystem():
        with open('test.toml', 'w') as toml_file:
            toml_file.write("BAD MOJO")

        with pytest.raises(CliException):
            assert load_toml_config("test.toml")


def test_load_toml_config_pass():
    with CliRunner().isolated_filesystem():
        with open('test.toml', 'w') as toml_file:
            toml_file.write(f"[{COMMAND_NAME}]\nvariable = 13")

        assert {"variable": 13} == load_toml_config("test.toml")


@pytest.mark.parametrize("options,excluded_options,arguments,expected", [
    # options, excluded_options, arguments, expected
    ([], [], {}, ""),
    ([Option(["--apple"])], [], {"apple": 42}, "apple:42"),
    ([Option(["--apple"]), Option(["--banana"])], [], {"banana": 13, "apple": 42},
     "apple:42,banana:13"),
    ([Option(["--apple"]), Option(["--banana"])], ["banana"],
     {"banana": 13, "apple": 42}, "apple:42"),
    ([Option(["--apple"], is_eager=True), Option(["--banana"])], [],
     {"banana": 13, "apple": 42}, "banana:13"),
])
def test_print_config(options, excluded_options, arguments, expected):
    def mock_render(settings, arguments_):
        _ = arguments
        return ",".join([f"{s}:{arguments_[s]}" for s in sorted(settings)])

    assert print_config(options, excluded_options, arguments, mock_render) == expected


EXPECTED_EMPTY_CONFIG = f"""# Sample {COMMAND_NAME} configuration file, by """ + \
    f"""default located at {DEFAULT_CONFIG_FILE_PATH}.
# Configuration options already set to the default value are commented-out.

[{COMMAND_NAME}]"""

EXPECTED_DEFAULT_CONFIG = EXPECTED_EMPTY_CONFIG + f"""

# This is a setting
# a = 13"""

EXPECTED_NONDEFAULT_CONFIG = EXPECTED_EMPTY_CONFIG + f"""

# This is a setting
a = 33"""


@pytest.mark.parametrize("settings,arguments,expected", [
    # settings,                                                   arguments,
    # expected
    ({},                                                          {},
     EXPECTED_EMPTY_CONFIG),
    ({"a": Option(["-a"], default=13, help="This is a setting")}, {"a": 13},
     EXPECTED_DEFAULT_CONFIG),
    ({"a": Option(["-a"], default=13, help="This is a setting")}, {"a": 33},
     EXPECTED_NONDEFAULT_CONFIG),
])
def test_render_toml_config(settings, arguments, expected):
    assert render_toml_config(settings, arguments) == expected


def test_show_version_fail(capsys):
    show_version(None, None, None)
    captured_out, captured_err = capsys.readouterr()
    assert captured_out == ""
    assert captured_err == ""


def test_show_version(capsys, version_message):
    class MockContext:
        resilient_parsing = False

        def exit(self):
            pass

    show_version(MockContext(), None, True)
    captured_out, captured_err = capsys.readouterr()
    assert captured_out == version_message
    assert captured_err == ""
