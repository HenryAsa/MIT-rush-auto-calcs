import pandas as pd
from typing import Optional


def slice_into_df(
        df: pd.DataFrame,
        start_index: Optional[int] = None,
        end_index: Optional[int] = None,
    ) -> pd.DataFrame:
    """
    Extract a slice from a DataFrame between specified indices.

    This function extracts a slice from a DataFrame, starting from
    `start_index` to `end_index`. If `start_index` or `end_index` is
    not provided, default values are used (0 for `start_index` and one
    less than the last index of the DataFrame for `end_index`).

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame from which to slice.
    start_index : Optional[int], default=None
        The index of the first row in the slice. Defaults to 0 if None.
    end_index : Optional[int], default=None
        The index of the last row in the slice. Defaults to one less
        than the DataFrame's last index if None or if the provided
        index is out of bounds.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the rows from `start_index` to
        `end_index`.

    Examples
    --------
    >>> import pandas as pd
    >>> data = {'col1': [1, 2, 3, 4, 5], 'col2': [10, 20, 30, 40, 50]}
    >>> df = pd.DataFrame(data)
    >>> slice_into_df(df, 1, 3)
       col1  col2
    1     2    20
    2     3    30
    3     4    40

    If `end_index` is None, it defaults to the second-to-last index:
    >>> slice_into_df(df)
       col1  col2
    0     1    10
    1     2    20
    2     3    30
    3     4    40

    If both `start_index` and `end_index` are None, it behaves similarly:
    >>> slice_into_df(df, None, None)
       col1  col2
    0     1    10
    1     2    20
    2     3    30
    3     4    40
    """
    if start_index is None:
        start_index = 0
    if end_index is None or end_index > len(df) - 2:
        end_index = len(df) - 2

    return df.iloc[start_index:end_index + 1]


def get_lap_indices(
        df: pd.DataFrame,
        start_lap: int,
        end_lap: int,
    ) -> dict[int: list[int, int]]:
    """
    Retrieve the start and end indices for given laps.

    This function takes a DataFrame containing race data and returns
    the start and end indices for the specified laps.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing race data, with at least a column 
        named 'Lap Number'.
    start_lap : int
        The starting lap number for which to find the indices.
    end_lap : int
        The ending lap number for which to find the indices.

    Returns
    -------
    dict[int, list[int, int]]
        A dictionary where keys are the lap numbers (start_lap and 
        end_lap) and values are lists containing the start and end 
        indices of those laps.

    Examples
    --------
    >>> data = {
    ...     'Lap Number': [1, 1, 2, 2, 3, 3],
    ...     'Speed': [100, 105, 98, 102, 97, 99]
    ... }
    >>> df = pd.DataFrame(data)
    >>> get_lap_indices(df, 1, 2)
    {1: [0, 1], 2: [2, 3]}

    Notes
    -----
    This function assumes that the DataFrame has a column named 
    'Lap Number' and that the laps are sequentially indexed.
    """
    lap_indices: dict[int, list[int, int]] = {}

    for lap_number in (start_lap, end_lap):
        lap_start_index = df.loc[df['Lap Number'] == lap_number].index[0]
        lap_end_index = df.loc[df['Lap Number'] == lap_number].index[-1]
        lap_indices[lap_number] = [lap_start_index, lap_end_index]

    return lap_indices