"""
Lap-Data Functions
==================
"""

import json
from typing import Optional

from geopy.distance import great_circle
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from race_analysis.constants import DATA_DIRECTORY

from .column_names import COL_LATITUDE, COL_LONGITUDE
from .df_utils import strip_df_of_units
from .time_utils import convert_time_list_to_seconds
from .utils import get_filename, get_files_with_extension


def get_lap_indices(
        df: pd.DataFrame,
        start_lap: Optional[int] = None,
        end_lap: Optional[int] = None,
    ) -> dict[int: tuple[int, int]]:
    """
    Retrieve the start and end indices for given laps.

    This function takes a DataFrame containing race data and returns
    the start and end indices for the specified laps.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing race data, with at least a column
        named 'Lap Number'.
    start_lap : Optional[int], default=None
        The starting lap number for which to find the indices.  By
        default, the second lap will be used as the starting lap if
        `start_lap` is not provided.
    end_lap : Optional[int], default=None
        The ending lap number for which to find the indices.  By
        default, the second-to-last lap will be used as the ending lap
        if `end_lap` is not provided.

    Returns
    -------
    dict[int, tuple[int, int]]
        A dictionary where keys are the lap numbers (start_lap and
        end_lap) and values are tuples containing the start and end
        indices of those laps.

    Notes
    -----
    This function assumes that the DataFrame has a column named
    'Lap Number' and that the laps are sequentially indexed.  If lap
    numbers are not provided, the second lap and second-to-last lap
    are assumed to be the start/end lap respectively (typically the
    first and laps have messy data, so by default they are excluded).

    Examples
    --------
    >>> data = {
    ...     'Lap Number': [1, 1, 2, 2, 3, 3],
    ...     'Speed': [100, 105, 98, 102, 97, 99]
    ... }
    >>> df = pd.DataFrame(data)
    >>> get_lap_indices(df, 1, 2)
    {1: (0, 1), 2: (2, 3)}

    >>> data = {
    ...     'Lap Number': [1, 1, 2, 2, 3, 3, 4, 4],
    ...     'Speed': [100, 105, 98, 102, 97, 99, 96, 101]
    ... }
    >>> df = pd.DataFrame(data)
    >>> get_lap_indices(df, 2, 3)
    {2: (2, 3), 3: (4, 5)}

    >>> data = {
    ...     'Lap Number': [1, 1, 2, 2, 3, 3, 4, 4],
    ...     'Speed': [100, 105, 98, 102, 97, 99, 96, 101]
    ... }
    >>> df = pd.DataFrame(data)
    >>> get_lap_indices(df)
    {2: (2, 3), 3: (4, 5)}
    """
    lap_num_column = 'Lap Number'
    lap_indices: dict[int, list[int, int]] = {}

    if start_lap is None:
        start_lap = 2
    if end_lap is None:
        end_lap = (df[lap_num_column].iloc[-1] - 1).magnitude

    for lap_number in range(start_lap, end_lap + 1):
        lap_start_index = df.loc[df[lap_num_column] == lap_number].index[0]
        lap_end_index = df.loc[df[lap_num_column] == lap_number].index[-1]
        lap_indices[lap_number] = (lap_start_index, lap_end_index)

    return lap_indices


def get_start_end_laps(df: pd.DataFrame) -> tuple[int, int]:
    """
    Calculate the start and end lap numbers for a race.

    This function takes a DataFrame containing lap information and
    returns a tuple with the start lap number and the end lap number.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing lap information. It should have a column
        named 'Lap Number'.

    Returns
    -------
    tuple of int
        A tuple containing:
        - start_lap_num: The start lap number (fixed as 2).
        - end_lap_num: The end lap number, derived from the last lap
          number in the DataFrame minus one.

    Notes
    -----
    The function assumes that the 'Lap Number' column exists and
    contains numeric values. The end lap number is calculated by
    subtracting 1 from the last value in the 'Lap Number' column.
    """
    start_lap_num = 2
    end_lap_num = (df['Lap Number'].iloc[-1] - 1).magnitude

    return start_lap_num, end_lap_num


def get_lap_times_from_json(
        dataset_name: str,
        lap_times_filepath: Optional[str] = None,
    ) -> list[float]:
    """
    Retrieve lap times from a JSON file for a specific dataset.

    This function reads lap times from a JSON file and returns them
    as a list of floats, representing the times in seconds. The JSON
    file should contain lap times for various datasets identified by
    their filenames.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to retrieve lap times for.
    lap_times_filepath : Optional[str], default=None
        The path to the JSON file containing lap times. If not
        provided, defaults to 'data/lap_times.json'.

    Returns
    -------
    list of float
        A list of lap times in seconds for the specified dataset.

    Raises
    ------
    NameError
        If the dataset name is not found in the JSON file.

    See Also
    --------
    add_lap_numbers_to_csv : Adds lap numbers to a CSV file based on
                             lap times.

    Notes
    -----
    The JSON file should have the following structure:

    .. code-block:: json

        {
            "dataset_01_filename": ["12.34", "13.56", "14.78"],
            "dataset_02_filename": ["11.22", "12.34", "13.45"]
        }


    Examples
    --------
    Retrieve lap times for a given dataset from the default JSON file:

    >>> get_lap_times_from_json('dataset_01')
    [12.34, 13.56, 14.78]

    Retrieve lap times from a specified JSON file:

    >>> get_lap_times_from_json('dataset_01', 'path/to/lap_times.json')
    [11.22, 12.34, 13.45]
    """
    data_filename = get_filename(dataset_name)

    lap_times_filepath = 'data/lap_times.json' if lap_times_filepath is None else lap_times_filepath

    with open(lap_times_filepath) as lap_times_file:
        all_lap_times = json.load(lap_times_file)

    if data_filename not in all_lap_times:
        raise NameError(f'"{data_filename}" was not in the lap_times.json file')

    return convert_time_list_to_seconds(all_lap_times[data_filename])


def add_lap_numbers_to_csv(
        csv_to_modify: str,
        new_csv_filename: Optional[str] = None,
        lap_times: Optional[list[float]] = None,
    ) -> None:
    """
    Adds lap numbers to a CSV file based on lap times.

    If lap times are not provided, they are fetched from the
    `lap_times.json` file associated with the CSV.

    Parameters
    ----------
    csv_to_modify : str
        The path to the CSV file to be modified.
    new_csv_filename : Optional[str], optional
        The filename for the new CSV file with lap numbers. If not
        provided, the original CSV file is overwritten.
    lap_times : Optional[list[float]], optional
        A list of lap times. If not provided, lap times are fetched
        from a JSON file.

    Returns
    -------
    None
        This function does not return any value, but either modifies
        the original CSV file or saves the CSV as a new file.

    See Also
    --------
    get_lap_times_from_json : Retrieve lap times from a JSON file for
                              a specific dataset.

    Examples
    --------
    Adding lap numbers to an existing CSV and saving it as a new file:

    >>> add_lap_numbers_to_csv('race_data.csv', 'race_data_with_laps.csv', [12.5, 14.3, 15.2])

    Adding lap numbers to an existing CSV and overwriting the original file:

    >>> add_lap_numbers_to_csv('race_data.csv', lap_times=[12.5, 14.3, 15.2])

    Adding lap numbers by fetching lap times from a JSON file:

    >>> add_lap_numbers_to_csv('race_data.csv')
    """
    if lap_times is None:
        lap_times = get_lap_times_from_json(get_filename(csv_to_modify))

    race_data = pd.read_csv(
        filepath_or_buffer=csv_to_modify,
        header=[0,1],
    )
    cumulative_lap_times = [sum(lap_times[:lap_num+1]) for lap_num in range(len(lap_times))]

    race_data[('Lap Number', 'dimensionless')] = len(cumulative_lap_times) - 1

    for current_lap in reversed(range(1, len(cumulative_lap_times))):
        race_data.loc[race_data[('Time', 's')] < cumulative_lap_times[current_lap], 'Lap Number'] = current_lap

    race_data.to_csv(csv_to_modify if new_csv_filename is None else new_csv_filename, index=False)


def set_lap_num_in_data_csv() -> None:
    """
    Sets lap numbers in all CSV files within the `"data/formatted"`
    directory.

    This function iterates over all CSV files in the specified data
    directory and adds lap numbers to each file by calling the
    `add_lap_numbers_to_csv` function.

    Returns
    -------
    None
        This function does not return any value, but does modify the
        original data files.

    See Also
    --------
    add_lap_numbers_to_csv : Adds lap numbers to a CSV file based on
                             lap times.

    Examples
    --------
    Set lap numbers in all CSV files in the data directory:

    >>> set_lap_num_in_data_csv()
    """
    for data_file in get_files_with_extension(DATA_DIRECTORY, '.csv'):
        add_lap_numbers_to_csv(data_file)


def reset_lap_times(lap_time_series: pd.Series) -> pd.Series:
    """
    Resets the lap times by subtracting the initial lap time.

    This function adjusts a series of lap times so that the first lap
    time is zero and each subsequent lap time is the difference from
    the first lap time.

    Parameters
    ----------
    lap_time_series : pd.Series
        A Pandas Series containing lap times.

    Returns
    -------
    pd.Series
        A Pandas Series with the initial lap time set to zero and
        subsequent lap times adjusted accordingly.

    Examples
    --------
    >>> import pandas as pd
    >>> lap_times = pd.Series([30.5, 31.0, 29.8, 32.1])
    >>> reset_lap_times(lap_times)
    0    0.0
    1    0.5
    2   -0.7
    3    1.6
    dtype: float64

    >>> lap_times2 = pd.Series([60.0, 62.5, 61.2, 63.4])
    >>> reset_lap_times(lap_times2)
    0    0.0
    1    2.5
    2    1.2
    3    3.4
    dtype: float64
    """
    return lap_time_series - lap_time_series[0]


def identify_starting_point(df: pd.DataFrame) -> tuple:
    """
    Identify the centroid of the most populated cluster in geographic
    data.

    This function uses DBSCAN clustering to group geographic
    coordinates and identifies the centroid of the most populated
    cluster, which might represent a significant location such as a
    start/finish line in a race.

    Parameters
    ----------
    df : pd.DataFrame
        A pandas DataFrame containing the columns 'GPS Latitude' and
        'GPS Longitude', representing geographical coordinates.

    Returns
    -------
    tuple
        A tuple representing the latitude and longitude of the
        centroid of the most populated cluster.

    Examples
    --------
    >>> data = {'GPS Latitude': [34.052235, 34.052235, 34.052235],
    ...         'GPS Longitude': [-118.243683, -118.243683, -118.243683]}
    >>> df = pd.DataFrame(data)
    >>> identify_starting_point(df)
    (34.052235, -118.243683)

    Notes
    -----
    - DBSCAN parameters: `eps` approximates to 50 meters (can be
      adjusted based on the specific dataset) and requires at least 10
      samples to form a cluster.
    - Ensure that the DataFrame does not include units in the
      coordinate columns and that they are appropriately named as 'GPS
      Latitude' and 'GPS Longitude'.
    """
    kms_per_radian = 6371.0088
    epsilon = 0.05 / kms_per_radian  # convert to radians for the haversine formula
    db = DBSCAN(eps=epsilon, min_samples=10, algorithm='ball_tree', metric='haversine').fit(
        np.radians(strip_df_of_units(df[[COL_LATITUDE, COL_LONGITUDE]], rename_cols_with_units=False)))
    cluster_labels = db.labels_

    largest_cluster = np.argmax(np.bincount(cluster_labels[cluster_labels >= 0]))

    # Compute the centroid of the largest cluster
    largest_cluster_indices = np.where(cluster_labels == largest_cluster)
    largest_cluster_points = df.iloc[largest_cluster_indices]
    centroid = (largest_cluster_points[COL_LATITUDE].mean(), largest_cluster_points[COL_LONGITUDE].mean())
    return centroid


def find_laps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign lap numbers and current lap times to GPS data in a
    DataFrame.

    This function processes a DataFrame containing 'Delta Time', 'GPS
    Latitude', and 'GPS Longitude' columns to identify laps in a race.
    It assigns a lap number to each point and calculates the current
    lap time based on the identified laps.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the race data with 'Delta Time', 'GPS
        Latitude', and 'GPS Longitude' columns.

    Returns
    -------
    pd.DataFrame
        The input DataFrame with added 'Lap Number' and 'Current Lap
        Time' columns.

    Notes
    -----
    The function uses a 0.05 km threshold to determine when the car
    passes the start/finish line.  It ensures that the lap time is at
    least 10 seconds long before counting a new lap to avoid false
    positives.

    Examples
    --------
    >>> import pandas as pd
    >>> from pint import UnitRegistry
    >>> ureg = UnitRegistry()
    >>> df = pd.DataFrame({
    ...     'Delta Time': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ...     'GPS Latitude': [52.5200, 52.5201, 52.5202, 52.5203, 52.5204,
    ...                      52.5205, 52.5206, 52.5207, 52.5208, 52.5209],
    ...     'GPS Longitude': [13.4050, 13.4051, 13.4052, 13.4053, 13.4054,
    ...                       13.4055, 13.4056, 13.4057, 13.4058, 13.4059]
    ... })
    >>> df['Delta Time'] = df['Delta Time'].pint.quantify('second')
    >>> df = find_laps(df)
    >>> df[['Lap Number', 'Current Lap Time']]
       Lap Number  Current Lap Time
    0           1               1.0
    1           1               2.0
    2           1               3.0
    3           1               4.0
    4           1               5.0
    5           1               6.0
    6           1               7.0
    7           1               8.0
    8           1               9.0
    9           2               0.0
    """
    if 'Lap Number' in df.columns:
        raise NameError('This DataFrame already contains a "Lap Number" column.')

    minimal_df = strip_df_of_units(df[['Delta Time', COL_LATITUDE, COL_LONGITUDE]], rename_cols_with_units=False)
    start_lat, start_lon = identify_starting_point(minimal_df)

    # Threshold for considering the car has passed the start/finish line (in kilometers)
    threshold = 0.05

    current_lap = 1
    current_lap_time = 0
    lap_numbers = []
    lap_times = []

    for index, row in minimal_df.iterrows():
        distance_from_start = great_circle((start_lat, start_lon), (row[COL_LATITUDE], row[COL_LONGITUDE])).kilometers

        is_new_lap = (
            distance_from_start <= threshold and    # Ensure distance from starting point is reasonable
            index > 0 and                           # Avoid counting the first point if it's close to the start
            (current_lap_time >= 10 or              # Ensure the current lap is at least 10 seconds long
             current_lap == 1)                      # Or skip this check if this is the first lap
        )
        current_lap_time += row['Delta Time']

        if is_new_lap:  # Avoid counting the first point if it's close to the start
            current_lap += 1
            current_lap_time = 0

        lap_numbers.append(current_lap)
        lap_times.append(current_lap_time)

    df['Lap Number'] = pd.Series(data=lap_numbers, name='Lap Number', dtype='pint[dimensionless]')
    df['Current Lap Time'] = pd.Series(data=lap_times, name='Lap Time', dtype='pint[second]')

    return df
