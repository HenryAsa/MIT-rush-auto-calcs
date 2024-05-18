"""
Race Analysis Functions
=======================

Methods to import and initialize race data for analysis.
"""

import pandas as pd

from .column_names import COL_LAP_NUM
from .columns import initialize_channels
from .laps_data import find_laps
from .utils import get_filename


def generate_units_dict(
        csv_filepath: str,
        units: dict[str, str]
    ) -> dict[str, str]:
    """
    Generate a dictionary of units from a CSV file.

    This function reads the first row of a CSV file specified by the
    file path.  It then generates and returns a dictionary where each
    key-value pair corresponds to a column label and its associated
    unit.  If a unit is not specified (empty or consisting only of
    spaces) for a label, it is replaced with 'dimensionless'.
    Additionally, any spaces are removed from the units, and
    percentage symbols are replaced with the word 'percent'.

    Parameters
    ----------
    csv_filepath : str
        The file path to the CSV file from which units are to be
        extracted.
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Returns
    -------
    dict[str, str]
        A dictionary where each key is a column label from the CSV and
        each value is the cleaned unit associated with that label.
        'Dimensionless' is used for labels without specified units.

    Examples
    --------
    >>> generate_units_dict('data.csv')
    {'Temperature': 'Celsius', 'Humidity': 'percent', 'Pressure': 'dimensionless'}
    """
    units_data = pd.read_csv(
        filepath_or_buffer=csv_filepath,
        nrows=1,
    ).to_dict(orient='list')

    for label, unit in units_data.items():
        if unit[0].replace(' ', '') == '':
            unit[0] = 'dimensionless'
        units[label] = unit[0].replace(' ', '').replace('%', 'percent')

    return units


def load_race(
        race_data_filepath: str,
        units: dict[str, str]
    ) -> pd.DataFrame:
    """
    Load race data from a CSV file and quantify the units using Pint.

    This function reads race data from a specified CSV file.  The CSV
    file is expected to have a multi-level header, with the first
    level being the data labels and the second level being the units.
    After loading the data, it uses the `generate_units_dict` function
    to process and clean the units from the same CSV file.  Finally,
    the function applies Pint's quantify method to the data frame,
    which assigns the units to the data based on the second level of
    the header, allowing for unit-aware calculations.

    Parameters
    ----------
    race_data_filepath : str
        The file path to the CSV file containing the race data.
    units : dict[str, str]
        Dictionary mapping column name keys to the units the column's
        data is stored in.

    Returns
    -------
    pandas.DataFrame
        A pandas DataFrame containing the race data, with units
        applied to the data according to the second header row of the
        CSV file.  This DataFrame is compatible with Pint for
        unit-aware calculations.

    See Also
    --------
    generate_units_dict : Function to generate and clean the units
                          dictionary from the CSV file.
    initialize_channels : Function to initialize channels in the
                          DataFrame.
    find_laps : Function to find and compute lap numbers in the
                DataFrame.

    Notes
    -----
    The function sets the `attrs` attribute of the returned DataFrame
    with metadata containing the file path and file name of the
    loaded CSV file. This can be useful for tracking the data source.

    Examples
    --------
    >>> RACE_DATA_DF = load_race('race_data.csv')
    >>> RACE_DATA_DF.dtypes
    <output showing data types and units>
    """
    race_data = pd.read_csv(
        filepath_or_buffer=race_data_filepath,
        header=[0,1],
    )

    generate_units_dict(csv_filepath=race_data_filepath, units=units)

    race_data_df: pd.DataFrame = race_data.pint.quantify(level=-1)

    initialize_channels(race_data=race_data_df, units=units)

    if COL_LAP_NUM not in race_data_df.columns:
        find_laps(race_data_df)
        raise NameError('"Lap Number" column is not included in the DataFrame, so it was computed (but this computation might be wrong).')

    race_data_df.attrs = {
        "data_filepath": race_data_filepath,
        "data_filename": get_filename(race_data_filepath),
    }

    return race_data_df
