import csv
import json
from pathlib import Path
from typing import Any, cast

import pandas as pd
import yaml


def read_csv_file(path: Path) -> list[dict[str, Any]]:
    """
    Read a CSV file into a list of dictionaries.

    Parameters
    ----------
    path : Path
        Path to the CSV file.

    Returns
    -------
    list of dict
        Each row as a dictionary.
    """
    with path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def read_yaml_file(path: Path) -> list[dict[str, Any]]:
    """
    Read a YAML file into a list of dictionaries.

    Parameters
    ----------
    path : Path
        Path to the YAML file.

    Returns
    -------
    list of dict
        Parsed YAML content as a list. Wraps single mappings in a list.
    """
    with path.open(mode="r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("YAML root must be a dict or list of dicts")


def read_json_file(path: Path) -> list[dict[str, Any]]:
    """
    Read a JSON file into a list of dictionaries.

    Parameters
    ----------
    path : Path
        Path to the JSON file.

    Returns
    -------
    list of dict
        Parsed JSON content as a list. Wraps single dicts in a list.
    """
    with path.open(mode="r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("JSON root must be a dict or list of dicts")


def read_excel_file(path: Path, sheet_name: str | int = 0) -> list[dict[str, Any]]:
    """
    Read an Excel file into a list of dictionaries.

    Parameters
    ----------
    path : Path
        Path to the Excel file.
    sheet_name : str or int, optional
        Sheet name or index to read (default is first sheet).

    Returns
    -------
    list of dict
        Each row as a dictionary.
    """
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))


def read_file(path: Path, **kwargs) -> list[dict[str, Any]]:
    if path.suffix == "csv":
        return read_csv_file(path)
    elif path.suffix == "json":
        return read_json_file(path)
    elif path.suffix == "xlsx" or "xls":
        return read_excel_file(path, **kwargs)
    elif path.suffix == "yaml":
        return read_yaml_file
    else:
        raise ValueError(f"{path.suffix} files not supported.")
