"""Read and clean historical VN-Index data exported from Investing.com.

Supports the original Vietnamese column names and returns English-named numeric columns.
"""
import re

import numpy as np
import pandas as pd

COL_MAP = {
    "Lần cuối": "close",
    "Mở": "open",
    "Cao": "high",
    "Thấp": "low",
    "KL": "volume",
    "% Thay đổi": "pct_change",
}
DATE_CANDIDATES = ["Ngày", "Date", "date"]


def _to_number(x):
    """Convert strings such as '1.234,56', '1,234.56', '123,45M', and '-0,52%' to floats."""
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.number)):
        return float(x)
    s = str(x).strip().replace("%", "").replace("\xa0", "").replace(" ", "")
    if s in ("", "-"):
        return np.nan
    mult = 1.0
    if s[-1] in "KMBkmb":
        mult = {"K": 1e3, "M": 1e6, "B": 1e9}[s[-1].upper()]
        s = s[:-1]
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):          # European format: 1.234,56
            s = s.replace(".", "").replace(",", ".")
        else:                                     # US format: 1,234.56
            s = s.replace(",", "")
    elif "," in s:
        if re.fullmatch(r"-?\d{1,3}(,\d{3})+", s):  # 1,234 -> thousands separator
            s = s.replace(",", "")
        else:                                       # 12,34 -> decimal separator
            s = s.replace(",", ".")
    elif "." in s:
        if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):  # 1.234 -> thousands separator
            s = s.replace(".", "")
    return float(s) * mult


def find_data_file(root, name="vnindex.csv"):
    """Return data/<name>, or the only CSV file in data/ if the named file is missing."""
    from pathlib import Path
    data_dir = Path(root) / "data"
    target = data_dir / name
    if target.exists():
        return target
    csvs = sorted(data_dir.glob("*.csv"))
    if len(csvs) == 1:
        print(f"{name} not found; using the only file in data/: {csvs[0].name}")
        return csvs[0]
    found = [f.name for f in data_dir.iterdir()] if data_dir.exists() else "(data/ directory does not exist)"
    raise FileNotFoundError(
        f"Could not find {target}\nCurrent contents of data/: {found}\n"
        "Check the file name (Windows may hide extensions, resulting in vnindex.csv.csv) "
        "and make sure the file is in the data/ directory INSIDE the project.")


def load_vnindex(path):
    """Return a DataFrame with an ascending, unique date index and numeric English-named columns."""
    raw = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    raw.columns = [c.strip() for c in raw.columns]

    date_col = next((c for c in DATE_CANDIDATES if c in raw.columns), None)
    if date_col is None:  # The date column may not have a name
        date_col = next(c for c in raw.columns if c not in COL_MAP)

    # Investing.com dates use dd/mm/yyyy; let pandas infer the format if that does not match.
    dates = pd.to_datetime(raw[date_col], format="%d/%m/%Y", errors="coerce")
    if dates.isna().mean() > 0.5:
        dates = pd.to_datetime(raw[date_col], errors="coerce")

    df = raw.drop(columns=[date_col]).rename(columns=COL_MAP)
    df = df[[c for c in COL_MAP.values() if c in df.columns]]
    df = df.apply(lambda col: col.map(_to_number))
    df.index = pd.DatetimeIndex(dates, name="date")

    n_bad_dates = int(df.index.isna().sum())
    df = df[df.index.notna()].sort_index()
    n_dup = int(df.index.duplicated().sum())
    df = df[~df.index.duplicated(keep="last")]
    n_missing_close = int(df["close"].isna().sum())
    df = df.dropna(subset=["close"])

    df.attrs.update(n_bad_dates=n_bad_dates, n_duplicates=n_dup,
                    n_missing_close=n_missing_close)
    return df
