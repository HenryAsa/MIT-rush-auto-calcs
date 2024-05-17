import pandas as pd
from typing import Optional


def convert_to_magnitude(
        data: pd.DataFrame | pd.Series,
        units: str,
    ) -> pd.DataFrame | pd.Series:
    """
    Convert the values in a DataFrame or Series to specified units.

    This function uses the Pint package and Pint UnitRegistry to
    convert the values in the given DataFrame or Series to the
    specified units.

    Parameters
    ----------
    data : pd.DataFrame or pd.Series
        The data containing values to be converted.
    units : str
        The target units to which the values should be converted.

    Returns
    -------
    pd.DataFrame or pd.Series
        The data with values converted to the specified units.

    Notes
    -----
    This function does not modify the original DataFrame or Series.
    It returns a new DataFrame or Series with the converted values.

    Examples
    --------
    >>> from pint import UnitRegistry
    >>> import pandas as pd
    >>> ureg = UnitRegistry()
    >>> Q_ = ureg.Quantity
    >>> df = pd.DataFrame({
    ...     'length': [Q_(1, 'meter'), Q_(100, 'centimeter'), Q_(1000, 'millimeter')],
    ...     'mass': [Q_(1, 'kilogram'), Q_(1000, 'gram'), Q_(1, 'tonne')]
    ... })
    >>> convert_to_magnitude(df['length'], 'meter')
    0    1.0
    1    1.0
    2    1.0
    Name: length, dtype: float64

    >>> convert_to_magnitude(df['mass'], 'kilogram')
    0    1.0
    1    1.0
    2    1000.0
    Name: mass, dtype: float64
    """
    return data.apply(lambda val: val.to(units).value)


def magnitude_of_df_col(
        column_name: str,
        df: pd.DataFrame,
        units: dict[str, str]
    ) -> pd.DataFrame | pd.Series:
    """
    Convert the values of a specified column in a DataFrame to specified units.

    This function converts the values in a specified column of the given
    DataFrame to the units defined in the units dictionary.  It utilizes the
    `convert_to_magnitude` function which employs the Pint package for
    unit conversions.

    Parameters
    ----------
    column_name : str
        The name of the column in the DataFrame whose values are to be converted.
    df : pd.DataFrame
        The DataFrame containing the column with values to be converted.
    units : dict[str, str]
        A dictionary where keys are column names and values are the target units
        for conversion.

    Returns
    -------
    pd.DataFrame or pd.Series
        The specified column with values converted to the specified units.

    Notes
    -----
    This function does not modify the original DataFrame.  It returns a new
    DataFrame or Series with the converted values of the specified column.

    Examples
    --------
    >>> from pint import UnitRegistry
    >>> import pandas as pd
    >>> ureg = UnitRegistry()
    >>> Q_ = ureg.Quantity
    >>> df = pd.DataFrame({
    ...     'length': [Q_(1, 'meter'), Q_(100, 'centimeter'), Q_(1000, 'millimeter')],
    ...     'mass': [Q_(1, 'kilogram'), Q_(1000, 'gram'), Q_(1, 'tonne')]
    ... })
    >>> units = {'length': 'meter', 'mass': 'kilogram'}
    >>> magnitude_of_df_col('length', df, units)
    0    1.0
    1    1.0
    2    1.0
    Name: length, dtype: float64

    >>> magnitude_of_df_col('mass', df, units)
    0       1.0
    1       1.0
    2    1000.0
    Name: mass, dtype: float64
    """
    return convert_to_magnitude(df[column_name], units[column_name])


def strip_df_of_units(
        data_df: pd.DataFrame | pd.Series,
        rename_cols_with_units: bool = True
    ) -> pd.DataFrame | pd.Series:
    """
    Strip units from a pandas DataFrame or Series object, with an
    option to rename columns/series to include original unit
    information.

    This function processes pandas objects that have Pint quantities
    (data associated with units), converting all quantities to their
    base units.  Optionally, it appends the original unit information
    to the names of each column in a DataFrame or the name of a
    Series.  The renaming can be controlled by the
    `rename_cols_with_units` parameter.

    Parameters
    ----------
    data_df : pd.DataFrame | pd.Series
        The pandas DataFrame or Series to be stripped of units.  Must
        contain Pint quantities.
    rename_cols_with_units : bool, optional
        If True (default), the column or series names will be updated
        to include the original unit information.  If False, names
        will remain unchanged.

    Returns
    -------
    pd.DataFrame | pd.Series
        A new DataFrame or Series with all quantities converted to
        base units.  If `rename_cols_with_units` is True, the original
        units are appended to the column/series names; otherwise, the
        names are unchanged.

    Raises
    ------
    TypeError
        If `data_df` is neither a pandas DataFrame nor a Series.

    Examples
    --------
    >>> import pandas as pd
    >>> import pint_pandas
    >>> ureg = pint_pandas.PintTypeRegistry()
    >>> data = {'length': [1, 2, 3] * ureg.meter, 'time': [10, 20, 30] * ureg.second}
    >>> df = pd.DataFrame(data)
    >>> strip_df_of_units(df)
    >>> strip_df_of_units(df, rename_cols_with_units=False)
    """
    incorrect_type_error = TypeError(f'data_df must be a pd.Dataframe or a pd.Series, but instead it is of type "{type(data_df)}"')

    if isinstance(data_df, pd.DataFrame):
        if rename_cols_with_units is True:
            column_names = {original_name: f'{original_name} ({series.pint.to_base_units().units})' for original_name, series in data_df.items()}
            return data_df.copy().rename(columns=column_names).pint.to_base_units().pint.magnitude

        new_df: pd.DataFrame = data_df.copy().pint.dequantify()
        new_df.columns = [col[0] for col in new_df.columns.values]
        return new_df

    if isinstance(data_df, pd.Series):
        if rename_cols_with_units is True:
            name = f'{data_df.name} ({data_df.pint.to_base_units().pint.units})'
        else:
            name = data_df.name

        return pd.Series(name=name, data=data_df.copy().pint.to_base_units().pint.magnitude)

    raise incorrect_type_error


def slice_into_df(
        df: pd.DataFrame,
        start_index: Optional[int] = None,
        end_index: Optional[int] = None,
    ) -> pd.DataFrame:
    """
    Extract a slice from a DataFrame between specified indices.

    This function extracts a slice from a DataFrame, starting from
    `start_index` to `end_index`.  If `start_index` or `end_index` is
    not provided, default values are used (0 for `start_index` and one
    less than the last index of the DataFrame for `end_index`).

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame from which to slice.
    start_index : Optional[int], default=None
        The index of the first row in the slice.  Defaults to 0 if None.
    end_index : Optional[int], default=None
        The index of the last row in the slice.  Defaults to one less
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


def columns_during_state(
        df: pd.DataFrame,
        data_columns: str | list[str],
        state_columns: str | list[str],
        fill_with_zeros: bool = False,
        all_states_must_be_on: bool = True,
    ) -> pd.DataFrame:
    """
    Filter data columns based on state columns' conditions.

    This function filters the specified data columns in a DataFrame
    based on the conditions defined by state columns.  It allows
    customization to fill non-matching rows with zeros or leave them
    as NaN, and to specify whether all state columns must be on or if
    any can be on.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the data and state columns.
    data_columns : str or list of str
        The column(s) to be filtered based on the state columns.
    state_columns : str or list of str
        The column(s) that define the state conditions, containing
        only 0 and 1 values.
    fill_with_zeros : bool, optional
        If True, non-matching rows in data columns are filled with
        zerosOtherwise, they are filled with NaNDefault is False.
    all_states_must_be_on : bool, optional
        If True, rows where all state columns are 1 are selected.
        If False, rows where any state column is 1 are selected.
        Default is True.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the filtered data columns.

    Raises
    ------
    ValueError
        If any of the data or state columns are not present in the
        DataFrame, or if the state columns contain values other than
        0 and 1.

    Examples
    --------
    >>> import pandas as pd
    >>> data = {
    ...     'A': [1, 2, 3, 4],
    ...     'B': [5, 6, 7, 8],
    ...     'State1': [1, 0, 1, 1],
    ...     'State2': [1, 1, 0, 1]
    ... }
    >>> df = pd.DataFrame(data)
    >>> columns_during_state(df, ['A', 'B'], ['State1', 'State2'])
       A    B
    0  1  5.0
    1  NaN NaN
    2  NaN NaN
    3  4.0  8.0

    >>> columns_during_state(df, 'A', 'State1', fill_with_zeros=True)
       A
    0  1
    1  0
    2  3
    3  4

    >>> columns_during_state(df, ['A', 'B'], 'State2', all_states_must_be_on=False)
       A    B
    0  1  5
    1  NaN NaN
    2  3  7
    3  4  8
    """
    data_columns = [data_columns] if isinstance(data_columns, str) else data_columns
    state_columns = [state_columns] if isinstance(state_columns, str) else state_columns

    if not set(data_columns).issubset(df.columns):
        raise ValueError(f'The following data columns are not present in the DataFrame: {set(data_columns) - set(df.columns)}')
    if not set(state_columns).issubset(df.columns):
        raise ValueError(f'The following state columns are not present in the DataFrame: {set(state_columns) - set(df.columns)}')

    for state_column in state_columns:
        if not df[state_column].isin([0, 1]).all():
            raise ValueError(f'State column "{state_column}" must only contain 0 and 1 values.')


    if all_states_must_be_on:
        is_on = df[state_columns].all(axis=1)
    else:
        is_on = df[state_columns].any(axis=1)

    if fill_with_zeros:
        default_value = 0
        new_df = df[data_columns].where(is_on, other=default_value)
    else:
        new_df = df[data_columns].where(is_on)

    return new_df
