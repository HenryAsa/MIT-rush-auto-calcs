"""
Pandas DataFrame Utility Functions
==================================

Extension functions that streamline Pandas DataFrame operations,
units-handling, and manipulating data within the DataFrames.
"""

from typing import Hashable, Optional
import pandas as pd

from race_analysis.column_names import COL_LAP_NUM
from race_analysis.units import Q_


def convert_series_to_magnitude(
        data: pd.Series,
        units: Optional[str] = None,
    ) -> pd.Series:
    """
    Convert the values in a Series to specified units.

    This function uses the Pint package and Pint UnitRegistry to
    convert the values in the given Series to the specified units.

    Parameters
    ----------
    data : pd.Series
        The data containing values to be converted.
    units : str, optional
        The target units to which the values should be converted.  If
        no units are defined, the column will simply be converted to
        the non-dimensional version of its current units.

    Returns
    -------
    pd.Series
        The data with values converted to the specified units.

    Notes
    -----
    This function does not modify the original Series.  It returns a
    new Series with the converted values.

    Examples
    --------
    >>> from pint import UnitRegistry
    >>> import pandas as pd
    >>> ureg = UnitRegistry()
    >>> Q_ = ureg.Quantity
    >>> data = pd.Series([Q_(1, 'meter'), Q_(100, 'centimeter'), Q_(1000, 'millimeter')])
    >>> convert_series_to_magnitude(data, 'meter')
    0    1.0
    1    1.0
    2    1.0
    dtype: float64

    >>> data = pd.Series([Q_(1, 'kilogram'), Q_(1000, 'gram'), Q_(1, 'tonne')])
    >>> convert_series_to_magnitude(data, 'kilogram')
    0       1.0
    1       1.0
    2    1000.0
    dtype: float64

    >>> data = pd.Series([Q_(1, 'second'), Q_(1, 'minute'), Q_(1, 'hour')])
    >>> convert_series_to_magnitude(data, 'second')
    0       1.0
    1      60.0
    2    3600.0
    dtype: float64

    >>> data = pd.Series([Q_(1, 'meter/second'), Q_(3.6, 'kilometer/hour')])
    >>> convert_series_to_magnitude(data, 'meter/second')
    0    1.0
    1    1.0
    dtype: float64
    """
    if units is None:
        return data.pint.magnitude

    return data.pint.m_as(units)


def magnitude_of_df_columns(
        df: pd.DataFrame,
        column_names: Optional[str | list[str]] = None,
        units: Optional[dict[str, str]] = None,
    ) -> pd.DataFrame | pd.Series:
    """
    Convert the values of specified columns in a DataFrame to
    specified units.

    This function converts the values in one or more specified columns
    of the given DataFrame to the units defined in the units
    dictionary.  It utilizes the `convert_series_to_magnitude` function which
    employs the Pint package for unit conversions.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the columns with values to be
        converted.
    column_names : str | list[str], optional
        The name or list of names of the columns in the DataFrame
        whose values are to be converted.  If no columns are
        specified, all of the columns in the DataFrame will be used.
    units : dict[str, str], optional
        A dictionary where keys are column names and values are the
        target units for conversion.  If no units dictionary is
        defined, the columns will simply be converted to the
        non-dimensional version of their current units.

    Returns
    -------
    pd.DataFrame or pd.Series
        The specified columns with values converted to the specified
        units.  If a single column name is provided, a Series is
        returned.  If a list of column names is provided, a DataFrame
        is returned.

    Raises
    ------
    ValueError
        If any of the specified columns are not present in the
        DataFrame.
    TypeError
        If column_names is not a string or list of strings.

    Notes
    -----
    This function does not modify the original DataFrame.  It returns
    a new DataFrame or Series with the converted values of the
    specified columns.

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
    >>> magnitude_of_df_columns('length', df, units)
    0    1.0
    1    1.0
    2    1.0
    Name: length, dtype: float64

    >>> magnitude_of_df_columns(['length', 'mass'], df, units)
       length  mass
    0     1.0   1.0
    1     1.0   1.0
    2     1.0   1000.0
    """
    if column_names is None:
        column_names = df.columns

    if isinstance(column_names, str):
        conversion_units = None if units is None else units[column_names]
        return copy_attrs_to_new_df(original_df=df, new_df=convert_series_to_magnitude(df[column_names], conversion_units))

    elif isinstance(column_names, list):
        if not set(column_names).issubset(df.columns):
            raise ValueError(f'The following columns are not present in the DataFrame: {set(column_names) - set(df.columns)}')

        converted_df = pd.DataFrame()
        for column in column_names:
            conversion_units = None if units is None else units[column]
            converted_df[column] = convert_series_to_magnitude(df[column], conversion_units)
        return copy_attrs_to_new_df(original_df=df, new_df=converted_df)

    raise TypeError(f'Column Names must be a string or a list of strings, but it was type {type(column_names)}')


def strip_df_of_units(
        data_df: pd.DataFrame | pd.Series,
        rename_cols_with_units: bool = True,
    ) -> pd.DataFrame | pd.Series:
    """
    Strip units from a pandas DataFrame or Series object, with an
    option to rename columns/series to include original unit
    information.  Mainly used for data exporting.

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
        return copy_attrs_to_new_df(original_df=data_df, new_df=new_df)

    if isinstance(data_df, pd.Series):
        if rename_cols_with_units is True:
            name = f'{data_df.name} ({data_df.pint.to_base_units().pint.units})'
        else:
            name = data_df.name

        return copy_attrs_to_new_df(original_df=data_df, new_df=pd.Series(name=name, data=data_df.copy().pint.to_base_units().pint.magnitude))

    raise incorrect_type_error


def slice_into_df(
        df: pd.DataFrame,
        start_index: Optional[int] = None,
        end_index: Optional[int] = None,
    ) -> pd.DataFrame | pd.Series:
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
        The index of the first row in the slice.  Defaults to 0 if
        None.
    end_index : Optional[int], default=None
        The index of the last row in the slice.  Defaults to one less
        than the DataFrame's last index if None or if the provided
        index is out of bounds.

    Returns
    -------
    pd.DataFrame or pd.Series
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

    return copy_attrs_to_new_df(original_df=df, new_df=df.iloc[start_index:end_index + 1])


def columns_during_state(
        df: pd.DataFrame,
        data_columns: str | list[str],
        state_columns: str | list[str],
        append_to_column_name: str = "",
        fill_with_zeros: bool = False,
        all_states_must_be_on: bool = True,
    ) -> pd.DataFrame | pd.Series:
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
        The input pint dimensionalized DataFrame containing data and
        state columns.
    data_columns : str | list[str]
        The column(s) to be filtered based on the state columns.
    state_columns : str | list[str]
        The column(s) that define the state conditions, containing
        only 0 and 1 values.
    append_to_column_name : str
        Appends the given string to all of the column names in the
        output DataFrame.
    fill_with_zeros : bool, optional
        If True, non-matching rows in data columns are filled with
        zerosOtherwise, they are filled with NaN.  Default is False.
    all_states_must_be_on : bool, optional
        If True, rows where all state columns are 1 are selected.
        If False, rows where any state column is 1 are selected.
        Default is True.

    Returns
    -------
    pd.DataFrame | pd.Series
        DataFrame containing data columns filtered by the state
        conditions.  If the DataFrame only contains a single column,
        the Series object is returned instead.  See Notes section for
        more details.

    Raises
    ------
    ValueError
        If any of the data or state columns are not present in the
        DataFrame, or if the state columns contain values other than
        0 and 1.

    Notes
    -----
    If only a single column is specified as the desired `data_column`,
    then this function will return a pd.Series object instead of a
    pd.DataFrame object.  If multiple data columns are requested, the
    output type will be a pd.DataFrame object.

    Examples
    --------
    >>> import pandas as pd
    >>> from pint import Quantity as Q_
    >>> df = pd.DataFrame({
    ...     'data1': pd.Series([1, 2, 3, 4], dtype='pint[meter]'),
    ...     'data2': pd.Series([5, 6, 7, 8], dtype='pint[sec]'),
    ...     'state1': pd.Series([1, 0, 1, 1], dtype='pint[dimensionless]'),
    ...     'state2': pd.Series([1, 1, 0, 1], dtype='pint[dimensionless]'),
    ... })

    When `fill_with_zeros` is False and `all_states_must_be_on` is True:
    >>> columns_during_state(df, ['data1', 'data2'], ['state1', 'state2'])
       data1  data2
    0      1      5
    1    nan    nan
    2    nan    nan
    3      4      8
    dtype: pint[meter], pint[sec]

    When `fill_with_zeros` is False and `all_states_must_be_on` is False:
    >>> columns_during_state(df, ['data1', 'data2'], ['state1', 'state2'], all_states_must_be_on=False)
       data1  data2
    0      1      5
    1      2      6
    2      3      7
    3      4      8
    dtype: pint[meter], pint[sec]

    When `fill_with_zeros` is True and `all_states_must_be_on` is True:
    >>> columns_during_state(df, 'data1', 'state1', fill_with_zeros=True)
       data1
    0      1
    1      0
    2      3
    3      4
    dtype: pint[meter]

    When `fill_with_zeros` is True and `all_states_must_be_on` is False:
    >>> columns_during_state(df, 'data1', 'state1', fill_with_zeros=True, all_states_must_be_on=False)
       data1
    0      1
    1      0
    2      3
    3      4
    dtype: pint[meter]
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

    state_df = magnitude_of_df_columns(df[state_columns], state_columns)

    if all_states_must_be_on:
        is_on = state_df.all(axis=1)
    else:
        is_on = state_df.any(axis=1)

    if fill_with_zeros:
        new_df = pd.DataFrame()
        for column in data_columns:
            default_value = Q_(0, df[column].pint.units)
            new_df[column] = df[column].where(is_on, other=default_value)
    else:
        new_df = df[data_columns].where(is_on)

    new_df.columns = [f'{column_name}{" " if append_to_column_name != "" else ""}{append_to_column_name.strip(" ")}' for column_name in new_df.columns]

    if len(new_df.columns) == 1:
        return copy_attrs_to_new_df(original_df=df, new_df=new_df[new_df.columns[0]])

    return copy_attrs_to_new_df(original_df=df, new_df=new_df)


def copy_attrs_to_new_df(
        original_df: pd.DataFrame | pd.Series,
        new_df: pd.DataFrame | pd.Series,
    ) -> pd.DataFrame | pd.Series:
    """
    Copy attributes from the original DataFrame or Series to a new
    DataFrame or Series.

    This function takes an original DataFrame or Series and a new
    DataFrame or Series, and copies the attributes from the original
    to the new one.  It returns the new DataFrame or Series with the
    copied attributes.

    Parameters
    ----------
    original_df : pd.DataFrame or pd.Series
        The DataFrame or Series from which attributes will be copied.
    new_df : pd.DataFrame or pd.Series
        The DataFrame or Series to which attributes will be copied.

    Returns
    -------
    pd.DataFrame or pd.Series
        The new DataFrame or Series with copied attributes.

    See Also
    --------
    pd.DataFrame.attrs : Access DataFrame attributes.
    pd.Series.attrs : Access Series attributes.

    Examples
    --------
    Copying attributes from one DataFrame to another:

    >>> import pandas as pd
    >>> df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> df1.attrs = {'author': 'user'}
    >>> df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
    >>> df2 = copy_attrs_to_new_df(df1, df2)
    >>> df2.attrs
    {'author': 'user'}

    Copying attributes from one Series to another:

    >>> s1 = pd.Series([1, 2, 3])
    >>> s1.attrs = {'description': 'sample series'}
    >>> s2 = pd.Series([4, 5, 6])
    >>> s2 = copy_attrs_to_new_df(s1, s2)
    >>> s2.attrs
    {'description': 'sample series'}
    """
    new_df.attrs = original_df.attrs
    return new_df


def normalize_column(
        df: pd.DataFrame,
        column_name: str,
        new_min: float,
        new_max: float,
        lap_num: Optional[int],
        normalized_units: Optional[str],
    ) -> pd.DataFrame:
    """
    Normalize a specified column in a DataFrame to a new range.

    This function normalizes the values of a specified column in a
    DataFrame to a new range defined by `new_min` and `new_max`.  If
    `lap_num` is provided, normalization is performed based on the
    values within the specified lap number; otherwise, normalization
    is based on the entire column.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the column to be normalized.
    column_name : str
        The name of the column to be normalized.
    new_min : float
        The new minimum value for the normalized column.
    new_max : float
        The new maximum value for the normalized column.
    lap_num : Optional[int]
        The lap number to filter the DataFrame by before normalizing.
        If None, the entire column is used.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the normalized column added.  The new
        column is named '{column_name} - Normalized'.

    Examples
    --------
    >>> import pandas as pd
    >>> import pint
    >>> ureg = pint.UnitRegistry()
    >>> df = pd.DataFrame({
    ...     'speed': [100, 150, 200, 250] * ureg.mph,
    ...     'lap': [1, 1, 2, 2]
    ... })
    >>> normalize_column(df, 'speed', 0, 1, lap_num=1)
       speed   lap  speed - Normalized
    0  100 mph    1          0.0
    1  150 mph    1          1.0
    2  200 mph    2          NaN
    3  250 mph    2          NaN

    >>> normalize_column(df, 'speed', 0, 1, lap_num=None)
       speed   lap  speed - Normalized
    0  100 mph    1          0.0
    1  150 mph    1          0.25
    2  200 mph    2          0.75
    3  250 mph    2          1.0
    """
    try:
        column_units = df[column_name].pint.units
        col_values = df[column_name].pint.magnitude
    except:
        column_units = None
        col_values = df[column_name]

    if lap_num is not None:
        lap_df = df[df[COL_LAP_NUM] == lap_num]
        lap_col_values = lap_df[column_name].pint.magnitude if column_units is not None else lap_df[column_name]
        min_val = lap_col_values.min()
        max_val = lap_col_values.max()
    else:
        min_val = col_values.min()
        max_val = col_values.max()

    normalized_values = ((col_values - min_val) / (max_val - min_val)) * (new_max - new_min) + new_min

    if normalized_units is not None:
        print(f'NORMALIZING DATA - SETTING NORMALIZED UNITS: SETTING TO {normalized_units}')
        normalized_column = pd.Series(data=normalized_values, dtype=f'pint[{normalized_units}]')
    elif column_units is not None:
        print(f'NORMALIZING DATA - KEEPING ORIGINAL COLUMN UNITS: SETTING TO {column_units}')
        normalized_column = pd.Series(data=normalized_values, dtype=f'pint[{column_units}]')
    else:
        print(f'NORMALIZING DATA - UNITLESS DATA WITH NO SPECIFIED UNITS, SO NORMALIZATION IS ALSO UNITLESS')
        normalized_column = normalized_values

    df[f'{column_name} - Normalized'] = normalized_column

    return df


def _get_nth_value(
        series_or_df: pd.DataFrame | pd.Series,
        precedes_value: Optional[float | dict[Hashable, float]] = None,
    ) -> float | dict[str, float]:
    """
    Helper function to filter values preceding a specified value in a
    Pandas Series or DataFrame.

    This function processes a Pandas Series or DataFrame, filtering
    values that precede a given value.  It also handles Pint units and
    PintArray objects.

    Parameters
    ----------
    series_or_df : pd.DataFrame or pd.Series
        Input data to be processed.
    precedes_value : float or dict[Hashable, float], optional
        A value or a dictionary of values used to filter the series.
        Only values preceding this will be considered.

    Returns
    -------
    tuple or dict[str, tuple]
        If the input is a Series, returns a tuple of the filtered
        series and units (if any).  If the input is a DataFrame,
        returns a dictionary with column names as keys and tuples of
        the filtered series and units as values.

    Raises
    ------
    TypeError
        If the input is not a Pandas Series or DataFrame.

    Notes
    -----
    - This function handles Pint units and PintArray objects.
    - If `precedes_value` is provided, only values before the
      specified value will be considered.

    Examples
    --------
    >>> import pandas as pd
    >>> from pint import UnitRegistry
    >>> ureg = UnitRegistry()
    >>> Q_ = ureg.Quantity

    >>> series = pd.Series([3, 1, 4, 1, 5, 9, 2])
    >>> _get_nth_value(series, precedes_value=4)
    (0    3
    1    1
    2    4
    dtype: int64, None)

    >>> df = pd.DataFrame({
    ...     'A': [3, 1, 4, 1, 5, 9, 2],
    ...     'B': [10, 20, 10, 30, 10, 40, 50]
    ... })
    >>> _get_nth_value(df, precedes_value={'A': 4, 'B': 30})
    {'A': (0    3
    1    1
    2    4
    Name: A, dtype: int64, None),
     'B': (0    10
    1    20
    2    10
    Name: B, dtype: int64, None)}
    """
    def _get_filtered_series(
            series: pd.Series,
            precedes_value: Optional[float] = None,
        ) -> pd.Series:
        if precedes_value is None:  return series

        try:
            target_value = precedes_value.magnitude
        except:
            target_value = precedes_value

        target_indices = series[series == target_value].index
        valid_indices = target_indices[target_indices > 0] - 1
        valid_indices = valid_indices[valid_indices.isin(series.index)]
        values_before_target = series.loc[valid_indices]

        return values_before_target

    def _get_computation_values(series: pd.Series) -> tuple:
        dtype = str(series.dtype)
        if dtype.startswith('pint['):
            return series.pint.magnitude, series.pint.units
        else:
            return series, None

    if isinstance(series_or_df, pd.Series):
        series, units = _get_computation_values(series_or_df)
        return (_get_filtered_series(series, precedes_value), units)

    elif isinstance(series_or_df, pd.DataFrame):
        result = {}
        for column in series_or_df.columns:
            series, units = _get_computation_values(series_or_df[column])
            result[column] = (_get_filtered_series(series, precedes_value), units)
        return result

    else:
        raise TypeError(f'Input must be a Pandas Series or DataFrame, but it was a {type(series_or_df)}')


def get_nth_smallest_value(
        series_or_df: pd.DataFrame | pd.Series,
        nth_smallest: int,
        precedes_value: Optional[float | dict[Hashable, float]] = None,
    ) -> float | dict[str, float]:
    """
    Get the nth smallest unique value from a Pandas Series or
    DataFrame.

    This function retrieves the nth smallest unique value from a given
    Pandas Series or DataFrame, optionally filtering values that
    precede a specified value.  It supports Pint units and PintArray
    objects in addition to non-dimensionalized Pandas objects.

    Parameters
    ----------
    series_or_df : pd.DataFrame or pd.Series
        Input data from which the nth smallest value is retrieved.
    nth_smallest : int
        The rank of the smallest value to retrieve.
    precedes_value : float or dict[Hashable, float], optional
        A value or a dictionary of values used to filter the series.
        Only values preceding this will be considered.

    Returns
    -------
    float or dict[str, float]
        The nth smallest unique value if the input is a Series, or a
        dictionary of nth smallest values for each column if the input
        is a DataFrame.

    Raises
    ------
    ValueError
        If the input does not contain enough unique values to satisfy
        the nth smallest requirement.
    TypeError
        If the input is not a Pandas Series or DataFrame.

    Notes
    -----
    - This function handles Pint units and PintArray objects.
    - If `precedes_value` is provided, only values before the
      specified value will be considered.

    See Also
    --------
    get_nth_largest_value : Sister function that returns the nth
                            largest value instead of the nth smallest
                            value.
    pd.Series.nsmallest : Return the first n smallest elements.
    pd.Series.unique : Return unique values of Series object.
    Pint : Pint is a Python package to define, operate and manipulate
           physical quantities: the product of a numerical value and a
           unit of measurement.
    PintArray : PintArray is an extension type for handling physical
                quantities with units in Pandas.

    Examples
    --------
    >>> import pandas as pd
    >>> from pint import UnitRegistry
    >>> ureg = UnitRegistry()
    >>> Q_ = ureg.Quantity

    >>> series = pd.Series([3, 1, 4, 1, 5, 9, 2])
    >>> get_nth_smallest_value(series, 2)
    2

    >>> df = pd.DataFrame({
    ...     'A': [3, 1, 4, 1, 5, 9, 2],
    ...     'B': [10, 20, 10, 30, 10, 40, 50]
    ... })
    >>> get_nth_smallest_value(df, 2)
    {'A': 2, 'B': 20}

    >>> series_with_units = pd.Series([Q_(3, 'm'), Q_(1, 'm'), Q_(4, 'm'), Q_(1, 'm')])
    >>> get_nth_smallest_value(series_with_units, 2)
    <Quantity(3, 'meter')>
    """
    if isinstance(series_or_df, pd.Series):
        filtered_series, units = _get_nth_value(series_or_df=series_or_df, precedes_value=precedes_value)
        nth_smallest_series = pd.Series(filtered_series.unique()).nsmallest(nth_smallest)

        if len(nth_smallest_series) < nth_smallest:
            raise ValueError(f'The input must have at least {nth_smallest} unique values.')

        nth_smallest_value = nth_smallest_series.iloc[-1]

        return nth_smallest_value if units is None else Q_(nth_smallest_value, units)

    elif isinstance(series_or_df, pd.DataFrame):
        result = {}
        filtered_data = _get_nth_value(series_or_df=series_or_df, precedes_value=precedes_value)
        for column, data in filtered_data.items():
            filtered_series, units = data
            nth_smallest_series = pd.Series(filtered_series.unique()).nsmallest(nth_smallest)

            if len(nth_smallest_series) < nth_smallest:
                result[column] = None
            else:
                nth_smallest_value = nth_smallest_series.iloc[-1]
                result[column] = nth_smallest_value if units is None else Q_(nth_smallest_value, units)

        return result

    else:
        raise TypeError(f'Input must be a Pandas Series or DataFrame, but it was a {type(series_or_df)}')


def get_nth_largest_value(
        series_or_df: pd.DataFrame | pd.Series,
        nth_largest: int,
        precedes_value: Optional[float | dict[Hashable, float]] = None,
    ) -> float | dict[str, float]:
    """
    Get the nth largest unique value from a Pandas Series or DataFrame.

    This function retrieves the nth largest unique value from a given
    Pandas Series or DataFrame, optionally filtering values that
    precede a specified value.  It supports Pint units and PintArray
    objects in addition to non-dimensionalized Pandas objects.

    Parameters
    ----------
    series_or_df : pd.DataFrame or pd.Series
        Input data from which the nth largest value is retrieved.
    nth_largest : int
        The rank of the largest value to retrieve.
    precedes_value : float or dict[Hashable, float], optional
        A value or a dictionary of values used to filter the series.
        Only values preceding this will be considered.

    Returns
    -------
    float or dict[str, float]
        The nth largest unique value if the input is a Series, or a
        dictionary of nth largest values for each column if the input
        is a DataFrame.

    Raises
    ------
    ValueError
        If the input does not contain enough unique values to satisfy
        the nth largest requirement.
    TypeError
        If the input is not a Pandas Series or DataFrame.

    Notes
    -----
    - This function handles Pint units and PintArray objects.
    - If `precedes_value` is provided, only values before the
      specified value will be considered.

    See Also
    --------
    get_nth_smallest_value : Sister function that returns the nth
                             smallest value instead of the nth largest
                             value.
    pd.Series.nlargest : Return the first n largest elements.
    pd.Series.unique : Return unique values of Series object.
    Pint : Pint is a Python package to define, operate and manipulate
           physical quantities: the product of a numerical value and a
           unit of measurement.
    PintArray : PintArray is an extension type for handling physical
                quantities with units in Pandas.

    Examples
    --------
    >>> import pandas as pd
    >>> from pint import UnitRegistry
    >>> ureg = UnitRegistry()
    >>> Q_ = ureg.Quantity

    >>> series = pd.Series([3, 1, 4, 1, 5, 9, 2])
    >>> get_nth_largest_value(series, 2)
    5

    >>> df = pd.DataFrame({
    ...     'A': [3, 1, 4, 1, 5, 9, 2],
    ...     'B': [10, 20, 10, 30, 10, 40, 50]
    ... })
    >>> get_nth_largest_value(df, 2)
    {'A': 5, 'B': 40}

    >>> series_with_units = pd.Series([Q_(3, 'm'), Q_(1, 'm'), Q_(4, 'm'), Q_(1, 'm')])
    >>> get_nth_largest_value(series_with_units, 2)
    <Quantity(3, 'meter')>
    """
    if isinstance(series_or_df, pd.Series):
        filtered_series, units = _get_nth_value(series_or_df=series_or_df, precedes_value=precedes_value)
        nth_largest_series = pd.Series(filtered_series.unique()).nlargest(nth_largest)

        if len(nth_largest_series) < nth_largest:
            raise ValueError(f'The input must have at least {nth_largest} unique values.')

        nth_largest_value = nth_largest_series.iloc[-1]

        return nth_largest_value if units is None else Q_(nth_largest_value, units)

    elif isinstance(series_or_df, pd.DataFrame):
        result = {}
        filtered_data = _get_nth_value(series_or_df=series_or_df, precedes_value=precedes_value)
        for column, data in filtered_data.items():
            filtered_series, units = data
            nth_largest_series = pd.Series(filtered_series.unique()).nlargest(nth_largest)

            if len(nth_largest_series) < nth_largest:
                result[column] = None
            else:
                nth_largest_value = nth_largest_series.iloc[-1]
                result[column] = nth_largest_value if units is None else Q_(nth_largest_value, units)

        return result

    else:
        raise TypeError(f'Input must be a Pandas Series or DataFrame, but it was a {type(series_or_df)}')
