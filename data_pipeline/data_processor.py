import logging
import pandas as pd


logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove duplicate rows."""
    before = len(df)
    new = df.drop_duplicates()
    logger.debug(f"Removed {before - len(new)} duplicate rows")
    return new


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        rows_dropped = df.dropna()
        logger.debug(f"Dropped {len(df) - len(rows_dropped)} rows")
        return rows_dropped
    elif axis == "columns":
        cols_dropped = df.dropna(axis=1)
        logger.debug(f"Dropped {len(df.columns) - len(cols_dropped.columns)} columns")
        return cols_dropped
    else:
        logger.error(f"Error, unsupported axis {axis}")
        raise ValueError



def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        logger.error(f"Unsupported outlier method: {method}")
        raise ValueError(f"Unsupported outlier method: {method}")

    numeric_cols = df.select_dtypes(include="number").columns

    for col in columns:
        if col not in df.columns:
            logger.warning(f"Column not found: {col}")
            continue
        if col not in numeric_cols:
            logger.warning(f"Column is not numeric: {col}")
            continue

        before = len(df)
        is_missing = df[col].isna()
        if method == "iqr":
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            keep = (df[col] >= lower) & (df[col] <= upper)
            bounds = f", lower={lower}, upper={upper}"
        else:
            z = (df[col] - df[col].mean()) / df[col].std()
            keep = z.abs() <= threshold
            bounds = ""

        df = df[keep | is_missing]
        logger.debug(f"{col}: method={method}, threshold={threshold}{bounds}, removed={before - len(df)}")

    return df
    


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config["processing"]

    if processing.get("remove_duplicates"):
        df = remove_duplicates(df)

    missing = processing.get("missing", {})
    if missing.get("enabled"):
        df = handle_missing(df, axis=missing.get("axis", "rows"))

    outliers = processing.get("outliers", {})
    if outliers.get("enabled"):
        df = remove_outliers(
            df,
            outliers["columns"],
            outliers["method"],
            outliers["threshold"],
        )

    return df


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before, columns_before = df_before.shape
    rows_after, columns_after = df_after.shape
    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }