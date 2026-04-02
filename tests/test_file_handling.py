from pathlib import Path

import pandas as pd
import pytest
import yaml

from telegraph.util.file_handling import (
    read_csv_file,
    read_data_file,
    read_excel_file,
    read_json_file,
    read_yaml_file,
)


def test_read_csv_file_returns_rows(tmp_path: Path) -> None:
    """CSV files should load as a list of row dictionaries."""
    path = tmp_path / "data.csv"
    path.write_text("name,count\nAlice,1\nBob,2\n")

    data = read_csv_file(path)

    assert data == [
        {"name": "Alice", "count": "1"},
        {"name": "Bob", "count": "2"},
    ]


def test_read_yaml_file_wraps_mapping(tmp_path: Path) -> None:
    """YAML mappings should be wrapped into a one-item list."""
    path = tmp_path / "data.yaml"
    path.write_text(yaml.dump({"name": "Alice"}))

    data = read_yaml_file(path)

    assert data == [{"name": "Alice"}]


def test_read_yaml_file_accepts_list(tmp_path: Path) -> None:
    """YAML lists should be returned unchanged."""
    path = tmp_path / "data.yaml"
    path.write_text(yaml.dump([{"name": "Alice"}, {"name": "Bob"}]))

    data = read_yaml_file(path)

    assert data == [{"name": "Alice"}, {"name": "Bob"}]


def test_read_yaml_file_rejects_scalar_root(tmp_path: Path) -> None:
    """YAML scalar roots should raise a validation error."""
    path = tmp_path / "data.yaml"
    path.write_text(yaml.dump("not-a-mapping"))

    with pytest.raises(ValueError, match="YAML root must be a dict or list"):
        read_yaml_file(path)


def test_read_json_file_wraps_mapping(tmp_path: Path) -> None:
    """JSON mappings should be wrapped into a one-item list."""
    path = tmp_path / "data.json"
    path.write_text('{"name": "Alice"}')

    data = read_json_file(path)

    assert data == [{"name": "Alice"}]


def test_read_json_file_accepts_list(tmp_path: Path) -> None:
    """JSON lists should be returned unchanged."""
    path = tmp_path / "data.json"
    path.write_text('[{"name": "Alice"}, {"name": "Bob"}]')

    data = read_json_file(path)

    assert data == [{"name": "Alice"}, {"name": "Bob"}]


def test_read_json_file_rejects_scalar_root(tmp_path: Path) -> None:
    """JSON scalar roots should raise a validation error."""
    path = tmp_path / "data.json"
    path.write_text('"not-a-mapping"')

    with pytest.raises(ValueError, match="JSON root must be a dict or list"):
        read_json_file(path)


def test_read_excel_file_returns_rows(tmp_path: Path) -> None:
    """Excel files should load as a list of row dictionaries."""
    path = tmp_path / "data.xlsx"
    pd.DataFrame(
        [{"name": "Alice", "count": 1}, {"name": "Bob", "count": 2}]
    ).to_excel(path, index=False)

    data = read_excel_file(path)

    assert data == [
        {"name": "Alice", "count": 1},
        {"name": "Bob", "count": 2},
    ]


def test_read_data_file_dispatches_by_suffix(tmp_path: Path) -> None:
    """read_data_file should dispatch to the correct reader by suffix."""
    csv_path = tmp_path / "data.csv"
    json_path = tmp_path / "data.json"
    yaml_path = tmp_path / "data.yaml"
    xlsx_path = tmp_path / "data.xlsx"

    csv_path.write_text("name\nAlice\n")
    json_path.write_text('[{"name": "Bob"}]')
    yaml_path.write_text(yaml.dump([{"name": "Carol"}]))
    pd.DataFrame([{"name": "Dana"}]).to_excel(xlsx_path, index=False)

    assert read_data_file(csv_path) == [{"name": "Alice"}]
    assert read_data_file(json_path) == [{"name": "Bob"}]
    assert read_data_file(yaml_path) == [{"name": "Carol"}]
    assert read_data_file(xlsx_path) == [{"name": "Dana"}]


def test_read_data_file_rejects_unsupported_suffix(tmp_path: Path) -> None:
    """Unsupported file suffixes should raise a validation error."""
    path = tmp_path / "data.txt"
    path.write_text("hello")

    with pytest.raises(ValueError, match=".txt files not supported"):
        read_data_file(path)
