from __future__ import annotations

import yaml

import pytest

from llmzk_tools.frontmatter import (
    _would_be_reinterpreted,
    dump_yaml_value,
    format_scalar,
    is_date_like,
    parse_frontmatter,
    quote_yaml_string,
    split_frontmatter_raw,
)


# --- quote_yaml_string ---


def test_quote_yaml_string_basic():
    assert quote_yaml_string("hello") == '"hello"'


def test_quote_yaml_string_double_quote_escaped():
    assert quote_yaml_string('say "hi"') == '"say \\"hi\\""'


def test_quote_yaml_string_backslash_escaped():
    result = quote_yaml_string("C:\\Users\\name")
    assert result == '"C:\\\\Users\\\\name"'


def test_quote_yaml_string_wikilink():
    assert quote_yaml_string("[[Source - Example]]") == '"[[Source - Example]]"'


def test_quote_yaml_string_pipe_alias():
    assert quote_yaml_string("[[Target|Alias]]") == '"[[Target|Alias]]"'


def test_quote_yaml_string_empty():
    assert quote_yaml_string("") == '""'


# --- quote_yaml_string round-trip safety ---


@pytest.mark.parametrize("value", [
    "simple",
    'with "quotes"',
    "C:\\Users\\name",
    "foo\\bar",
    "\\n\\t\\x30",
    "[[Source - Example]]",
    "[[Target|Alias]]",
    "path/with/slashes",
    "2026-07-17",
    "",
    "unicode: café — naïve",
])
def test_quote_yaml_string_round_trips(value: str):
    quoted = quote_yaml_string(value)
    parsed = yaml.safe_load(quoted)
    assert parsed == value


# --- format_scalar ---


def test_format_scalar_plain_string():
    assert format_scalar("hello") == "hello"


def test_format_scalar_wikilink_quoted():
    assert format_scalar("[[Source]]") == '"[[Source]]"'


def test_format_scalar_date_quoted():
    assert format_scalar("2026-07-17") == '"2026-07-17"'


def test_format_scalar_datetime_quoted():
    assert format_scalar("2026-07-17T12:34:56+01:00") == '"2026-07-17T12:34:56+01:00"'


def test_format_scalar_date_with_space_quoted():
    assert format_scalar("2026-07-17 13:53:59+01:00") == '"2026-07-17 13:53:59+01:00"'


def test_format_scalar_bool_true():
    assert format_scalar(True) == "true"


def test_format_scalar_bool_false():
    assert format_scalar(False) == "false"


def test_format_scalar_none():
    assert format_scalar(None) == ""


def test_format_scalar_int():
    assert format_scalar(42) == "42"


def test_format_scalar_path_quoted():
    assert format_scalar("00 Inbox/example.md") == '"00 Inbox/example.md"'


def test_format_scalar_pipe_unescaped_and_quoted():
    result = format_scalar("[[Target\\|Alias]]")
    assert result == '"[[Target|Alias]]"'


def test_format_scalar_backslash_quoted():
    result = format_scalar("C:\\path")
    assert "\\\\" in result


def test_format_scalar_datetime_object():
    import datetime as dt
    result = format_scalar(dt.datetime(2026, 7, 17, 12, 34, 56))
    assert result == '"2026-07-17T12:34:56"'


def test_format_scalar_date_object():
    import datetime as dt
    result = format_scalar(dt.date(2026, 7, 17))
    assert result == '"2026-07-17"'


# --- format_scalar round-trip safety ---


@pytest.mark.parametrize("value,expected", [
    ("simple", "simple"),
    ('with "quotes"', 'with "quotes"'),
    ("C:\\Users\\name", "C:\\Users\\name"),
    ("[[Source]]", "[[Source]]"),
    ("[[Target\\|Alias]]", "[[Target|Alias]]"),
    ("2026-07-17", "2026-07-17"),
    ("path/with/slashes", "path/with/slashes"),
])
def test_format_scalar_round_trips(value, expected):
    formatted = format_scalar(value)
    parsed = yaml.safe_load(formatted)
    assert parsed == expected


def test_format_scalar_bool_round_trips():
    assert yaml.safe_load(format_scalar(True)) is True
    assert yaml.safe_load(format_scalar(False)) is False


def test_format_scalar_int_round_trips():
    assert yaml.safe_load(format_scalar(42)) == 42


# --- is_date_like ---


def test_is_date_like_plain_date():
    assert is_date_like("2026-07-17")


def test_is_date_like_iso_datetime():
    assert is_date_like("2026-07-17T12:34:56")


def test_is_date_like_date_with_space():
    assert is_date_like("2026-07-17 12:34:56")


def test_is_date_like_not_date():
    assert not is_date_like("hello")


def test_is_date_like_partial_date():
    assert not is_date_like("2026-07")


def test_is_date_like_empty():
    assert not is_date_like("")


# --- split_frontmatter_raw ---


def test_split_frontmatter_raw_with_frontmatter():
    text = "---\ntype: concept\n---\n\n# Title\n"
    fm, body = split_frontmatter_raw(text)
    assert fm == "type: concept"
    assert body == "\n# Title\n"


def test_split_frontmatter_raw_no_frontmatter():
    text = "# Just body\n"
    fm, body = split_frontmatter_raw(text)
    assert fm is None
    assert body == text


def test_split_frontmatter_raw_empty_frontmatter():
    text = "---\n \n---\n\nBody\n"
    fm, body = split_frontmatter_raw(text)
    assert fm == " "


# --- parse_frontmatter ---


def test_parse_frontmatter_with_data():
    text = "---\ntype: concept\nstatus: seed\n---\n\n# Title\n"
    data, body, raw = parse_frontmatter(text)
    assert data == {"type": "concept", "status": "seed"}
    assert "# Title" in body
    assert raw == "type: concept\nstatus: seed"


def test_parse_frontmatter_no_frontmatter():
    text = "# Just body\n"
    data, body, raw = parse_frontmatter(text)
    assert data == {}
    assert body == text
    assert raw is None


def test_parse_frontmatter_yaml_error():
    text = "---\n: invalid: yaml:\n---\n\nBody\n"
    data, body, raw = parse_frontmatter(text)
    assert data == {}
    assert raw is not None


def test_parse_frontmatter_non_dict():
    text = "---\n- item\n- item2\n---\n\nBody\n"
    data, body, raw = parse_frontmatter(text)
    assert data == {}


def test_parse_frontmatter_empty_frontmatter():
    text = "---\n---\n\nBody\n"
    data, body, raw = parse_frontmatter(text)
    assert data == {}


# --- dump_yaml_value ---


def test_dump_yaml_value_scalar():
    lines: list[str] = []
    dump_yaml_value(lines, "key", "value")
    assert lines == ["key: value"]


def test_dump_yaml_value_quoted_scalar():
    lines: list[str] = []
    dump_yaml_value(lines, "key", "[[Source]]")
    assert lines == ['key: "[[Source]]"']


def test_dump_yaml_value_empty_list():
    lines: list[str] = []
    dump_yaml_value(lines, "key", [])
    assert lines == ["key: []"]


def test_dump_yaml_value_list_of_strings():
    lines: list[str] = []
    dump_yaml_value(lines, "key", ["a", "b"])
    assert lines == ["key:", "  - a", "  - b"]


def test_dump_yaml_value_list_of_quoted_strings():
    lines: list[str] = []
    dump_yaml_value(lines, "key", ["[[A]]", "[[B]]"])
    assert lines == ["key:", '  - "[[A]]"', '  - "[[B]]"']


def test_dump_yaml_value_none():
    lines: list[str] = []
    dump_yaml_value(lines, "key", None)
    assert lines == ["key:"]


def test_dump_yaml_value_bool():
    lines: list[str] = []
    dump_yaml_value(lines, "applied", True)
    assert lines == ["applied: true"]


def test_dump_yaml_value_int():
    lines: list[str] = []
    dump_yaml_value(lines, "schema_version", 1)
    assert lines == ["schema_version: 1"]


def test_dump_yaml_value_nested_dict():
    lines: list[str] = []
    dump_yaml_value(lines, "outer", {"inner": "val"})
    assert lines == ["outer:", "  inner: val"]


def test_dump_yaml_value_list_of_dicts():
    lines: list[str] = []
    dump_yaml_value(lines, "items", [{"a": "hello"}, {"b": "world"}])
    assert lines == ["items:", "  -", "    a: hello", "  -", "    b: world"]


def test_dump_yaml_value_date_string():
    lines: list[str] = []
    dump_yaml_value(lines, "created", "2026-07-17")
    assert lines == ['created: "2026-07-17"']


def test_dump_yaml_value_backslash_string():
    lines: list[str] = []
    dump_yaml_value(lines, "path", "C:\\Users")
    assert lines == ['path: "C:\\\\Users"']


def test_dump_yaml_value_indented():
    lines: list[str] = []
    dump_yaml_value(lines, "key", "val", indent=2)
    assert lines == ["  key: val"]


# --- dump_yaml_value round-trip safety ---


@pytest.mark.parametrize("key,value", [
    ("plain", "hello"),
    ("wikilink", "[[Source]]"),
    ("path", "00 Inbox/example.md"),
    ("date", "2026-07-17"),
    ("bool", True),
    ("int", 42),
    ("list", ["a", "b"]),
    ("quoted_list", ["[[A]]", "[[B]]"]),
    ("backslash", "C:\\Users\\name"),
])
def test_dump_yaml_value_round_trips(key: str, value):
    lines: list[str] = []
    dump_yaml_value(lines, key, value)
    yaml_text = "\n".join(lines)
    parsed = yaml.safe_load(yaml_text)
    assert parsed[key] == value


# --- YAML 1.1 keyword round-trip safety ---


@pytest.mark.parametrize("keyword", [
    "no", "yes", "on", "off",
    "No", "Yes", "On", "Off",
    "NO", "YES", "ON", "OFF",
    "true", "false", "True", "False",
    "TRUE", "FALSE",
    "null", "Null", "NULL", "~",
])
def test_format_scalar_quotes_yaml_bool_null_keywords(keyword: str):
    formatted = format_scalar(keyword)
    parsed = yaml.safe_load(formatted)
    assert parsed == keyword
    assert isinstance(parsed, str)


@pytest.mark.parametrize("number", [
    "123", "0", "00", "007", "01",
    "3.14", ".5", "12.",
    "0x1f", "0xFF", "0b101",
    "1_000", "-12", "+12", "-0",
])
def test_format_scalar_quotes_numeric_strings(number: str):
    formatted = format_scalar(number)
    parsed = yaml.safe_load(formatted)
    assert parsed == number
    assert isinstance(parsed, str)


# --- _would_be_reinterpreted ---


def test_would_be_reinterpreted_bool_keywords():
    assert _would_be_reinterpreted("no")
    assert _would_be_reinterpreted("yes")
    assert _would_be_reinterpreted("on")
    assert _would_be_reinterpreted("off")


def test_would_be_reinterpreted_null_keywords():
    assert _would_be_reinterpreted("null")
    assert _would_be_reinterpreted("~")


def test_would_be_reinterpreted_numbers():
    assert _would_be_reinterpreted("123")
    assert _would_be_reinterpreted("3.14")
    assert _would_be_reinterpreted("0x1f")


def test_would_be_reinterpreted_safe_strings():
    assert not _would_be_reinterpreted("hello")
    assert not _would_be_reinterpreted("seed")
    assert not _would_be_reinterpreted("active")


def test_would_be_reinterpreted_empty():
    assert _would_be_reinterpreted("")


def test_would_be_reinterpreted_yaml_error():
    assert _would_be_reinterpreted(": : :")
