from pathlib import Path

import logging
import pandas as pd
import json
import yaml

logger =  logging.getLogger(__name__)

def load_csv(filepath):
    """Load a CSV file into a DataFrame. filepath is a Path object."""
    data_path = Path(filepath)
    df = pd.read_csv(data_path)
    logger.info(f"Loaded file: {filepath}, DF length: {len(df)}")
    return df




def load_json(filepath):
    """Load a JSON file into a Python object (dict or list).
    filepath is a Path object.
    """
    with open(filepath) as f:
        js = json.load(f)
    logger.info(f"Loaded file: {filepath}")
    return js



def load_yaml(filepath):
    """Load a YAML file into a Python object.
    filepath is a Path object.
    """
    with open(filepath) as f:
        ym = yaml.safe_load(f)
    logger.info(f"Loaded file: {filepath}")
    return ym





def load_data(filepath):
    """Load a file based on its extension.
    filepath is a string, such as 'fixtures/sample.csv'
    """
    data_path = Path(filepath)
    suffix = data_path.suffix.lower()
    if suffix == ".csv":
        return load_csv(data_path)
    elif suffix == ".json":
        return load_json(data_path)
    elif suffix == ".yaml":
        return load_yaml(data_path)
    else:
        logger.error(f"Unsupported file format: {suffix}")
        raise ValueError
