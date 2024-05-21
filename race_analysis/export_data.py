"""
Data Exporting Functions
========================

Useful functions for exporting data or saving data in different
formats.
"""

import os
import re
from typing import Iterable, Optional

import pandas as pd
import pint
import scipy

from .df_utils import strip_df_of_units
from .utils import extract_text_within_parentheses, get_folder_from_filepath


def export_df_to_latex(
        df: pd.DataFrame | pd.Series,
        numeric_format: Optional[dict[str, str]] = None,
        units: Optional[dict[str, str | pint.Unit]] = None,
        default_round_amount: int = 2,
    ) -> str:
    """
    Export a DataFrame or Series to a LaTeX table with unit handling
    and formatting.

    This function converts a Pandas DataFrame or Series to a LaTeX
    table string, applying specified numeric formats and units to
    columns as needed.  It supports rounding and scientific notation,
    and can handle Pint units.

    Parameters
    ----------
    df : pd.DataFrame or pd.Series
        The DataFrame or Series to convert to a LaTeX table.
    numeric_format : dict of str, str, optional
        A dictionary specifying the numeric format for each column.
        Supported formats are ``'ROUND'`` and ``'SCIENTIFIC'``.  Can
        also use ``'ROUND(NUMBER)'`` or ``'SCIENTIFIC(NUMBER)'`` where
        ``NUMBER`` is an integer if the client wishes to define
        custom rounding for a specific column.
    units : dict of str, str or pint.Unit, optional
        A dictionary specifying the units for each column.  The keys
        are column names and the values are the units as strings or
        Pint Unit objects.
    default_round_amount : int, optional
        The default number of decimal places to round to if no
        specific rounding is provided in numeric_format.  Default is 2.

    Returns
    -------
    str
        A string containing the LaTeX representation of the DataFrame.

    See Also
    --------
    pandas.DataFrame.to_latex : Convert a DataFrame to a LaTeX
                                tabular object.

    Examples
    --------
    >>> import pandas as pd
    >>> import pint
    >>> from pint_pandas import PintType
    >>> ureg = pint.UnitRegistry()
    >>> df = pd.DataFrame({
    ...     'Length': [1.5, 2.5, 3.75] * ureg.meter,
    ...     'Weight': [50, 60, 75] * ureg.kilogram
    ... })
    >>> numeric_format = {'Length': 'ROUND(2)', 'Weight': 'SCIENTIFIC'}
    >>> units = {'Length': 'cm', 'Weight': ureg.gram}
    >>> latex_str = export_df_to_latex(df, numeric_format, units)
    >>> print(latex_str)
    \\begin{table*}
    \\begin{center}
    \\begin{tabular}{ll}
    \\toprule
     Length [centimeter] & Weight [gram] \\
    \\midrule
     150.00 & $5.00 \\times 10^{4}$ \\
     250.00 & $6.00 \\times 10^{4}$ \\
     375.00 & $7.50 \\times 10^{4}$ \\
    \\bottomrule
    \\end{tabular}
    \\end{center}
    \\end{table*}
    """
    new_df = pd.DataFrame()

    for column in df.columns:
        final_units = None

        if units is not None and column in units:
            final_units = units[column]
            data_with_dims = df[column].apply(lambda val: val.m_as(final_units))
        elif hasattr(df[column][0], 'units'):
            final_units = df[column].iloc[-3].units
            data_with_dims = df[column].apply(lambda val: val.m_as(final_units))
        else:
            data_with_dims = df[column]

        if numeric_format is not None and column in numeric_format:
            numeric_style = numeric_format[column]
            round_amount = default_round_amount if (column_round_amount := extract_text_within_parentheses(numeric_style)) is None else int(column_round_amount)

            if bool(re.match(r'^ROUND(\(\d+\))?$', numeric_style)):
                data_with_dims = data_with_dims.round(round_amount).apply(
                    lambda x: f'{x:,.{round_amount}f}'
                )
            elif bool(re.match(r'^SCIENTIFIC(\(\d+\))?$', numeric_style)):
                data_with_dims = data_with_dims.apply(
                    lambda x: (
                        f'${x:,.{round_amount}e}}}$'.replace(
                            'e', ' \\times 10^{'
                        ).replace(
                            '+0', ''
                        ).replace(
                            '+', ''
                        ).replace(
                            '-0', '-'
                        ).replace(
                            '-', '-'
                        )
                    )
                )

        elif isinstance(data_with_dims[0], (float, int)):
            data_with_dims = data_with_dims.round(default_round_amount).apply(
                lambda x: f'{x:,.{default_round_amount}f}'
            )

        column_name = f'{column}{"" if final_units is None else f" [{final_units}]"}'
        new_df[column_name] = data_with_dims

    table_top_wrapper = '\\begin{table*}\n\\begin{center}\n'
    table_bottom_wrapper = '\\end{center}\n\\end{table*}'

    return f'{table_top_wrapper}{new_df.to_latex(index=False)}{table_bottom_wrapper}'


def export_data_to_csv(
        time_df: pd.DataFrame | pd.Series,
        data_dfs: pd.DataFrame | Iterable[pd.Series],
        filename: str
    ) -> None:
    """
    Export time series data and associated data series to a CSV file.

    This function combines a time series (either a DataFrame or
    Series) with multiple data series, strips them of units using
    `strip_df_of_units`, and exports the resulting DataFrame to a CSV
    file.  The names of time and data series are updated to include
    original unit information.

    Parameters
    ----------
    time_df : pd.DataFrame | pd.Series
        The time series DataFrame or Series, which should include Pint
        quantities.  The time series data is used as the index in the
        exported CSV.
    data_dfs : pd.DataFrame | Iterable[pd.Series]
        An iterable of pandas Series objects representing the data to
        be exported alongside the time series.  Each series must have
        Pint quantities.
    filename : str
        The name of the file to which the combined data will be
        exported.

    Raises
    ------
    TypeError
        If `data_dfs` is not an Iterable of pd.Series or a pd.Series.

    Examples
    --------
    >>> import pandas as pd
    >>> import pint_pandas
    >>> ureg = pint_pandas.PintTypeRegistry()
    >>> time_data = pd.Series([1, 2, 3], name='time') * ureg.hour
    >>> data_series = pd.Series([4, 5, 6], name='speed') * ureg.meter / ureg.second
    >>> export_data_to_csv(time_data, data_series, 'output.csv')

    >>> export_data_to_csv(RACE_DATA_DF['Time'], [speed_during_coast, acceleration_during_coast, RACE_DATA_DF['GPS G Sum'], RACE_DATA_DF['GPS Latitude']], "some_data.csv")
    """
    incorrect_type_error = TypeError(f'data_dfs must be an Iterable of pd.Series or a pd.Series, but instead it is of type "{type(data_dfs)}"')
    export_df = pd.DataFrame()
    unitless_time_series = strip_df_of_units(time_df)
    export_df[unitless_time_series.name] = unitless_time_series

    if isinstance(data_dfs, pd.Series):
        data_dfs = [data_dfs]

    elif isinstance(data_dfs, pd.DataFrame):
        data_dfs = [series for _, series in data_dfs.copy().items()]

    if isinstance(data_dfs, Iterable):
        for column_data in data_dfs:
            assert isinstance(column_data, pd.Series), incorrect_type_error
            unitless_column = strip_df_of_units(column_data)
            export_df[unitless_column.name] = unitless_column
    else:
        raise incorrect_type_error

    os.makedirs(get_folder_from_filepath(filename), exist_ok=True)

    export_df.to_csv(filename)


def mat_to_csv(
        mat_filepath: str,
        csv_filepath: str,
    ) -> None:
    """
    Convert variables from a MATLAB .mat file to individual .csv files.

    This function loads each variable stored in a MATLAB .mat file and
    saves each as a separate .csv file.  The names of the .csv files
    are derived from the original .mat file's variable names appended
    to the original specified csv_filepath.  Metadata attributes in
    the .mat file, which start with '__', are ignored.

    Parameters
    ----------
    mat_filepath : str
        The path to the MATLAB .mat file to be converted.
    csv_filepath : str
        The base path for the output CSV files.  This base path will
        be appended with the name of each variable from the .mat file
        to create individual CSV file names.

    Returns
    -------
    None
        This function does not return any value but will print the
        path of each CSV file saved.

    Examples
    --------
    >>> mat_to_csv('example.mat', 'output.csv')
    Saved variable1 to output_variable1.csv
    Saved variable2 to output_variable2.csv

    Notes
    -----
    The function assumes all variables in the .mat file can be directly
    converted to a DataFrame.  Variables that contain MATLAB objects
    such as structures or cell arrays may require special handling not
    provided by this function.
    """
    # Load the .mat file
    mat_data = scipy.io.loadmat(mat_filepath)

    # Iterate over each key in the dictionary
    for key, value in mat_data.items():
        # Check if the key is one of the MATLAB variables and not a metadata attribute
        if not key.startswith('__'):
            # Convert the numpy array to a pandas DataFrame
            df = pd.DataFrame(value)
            # Construct CSV file path
            specific_csv_filepath = csv_filepath.replace('.csv', f'_{key}.csv')
            # Save DataFrame to CSV
            df.to_csv(specific_csv_filepath, index=False)
            print(f"Saved {key} to {specific_csv_filepath}")


def mats_to_csv(
        mat_files: Iterable[str],
        csv_filepath: str,
    ) -> None:
    """
    Convert variables from multiple MATLAB .mat files into a single
    .csv file.

    Each variable from the .mat files is loaded and stored in a single
    DataFrame.  Variables are renamed to ensure uniqueness across
    multiple files, typically by appending an index or file identifier
    to the original variable name.  The consolidated DataFrame is then
    saved to a single .csv file.

    Parameters
    ----------
    mat_filepaths : list of str
        A list of paths to the MATLAB .mat files to be converted.
    csv_filepath : str
        The path for the output .csv file that will contain the
        consolidated data.

    Returns
    -------
    None
        This function does not return any value but will save the
        consolidated data into a single CSV file.

    Examples
    --------
    >>> mats_to_csv(['file1.mat', 'file2.mat'], 'output.csv')
    Data from file1.mat and file2.mat saved to output.csv

    Notes
    -----
    Assumes that the .mat files contain variables that can be directly
    converted to DataFrames.  Variables containing MATLAB objects such
    as structures or cell arrays may require special handling.
    """
    data_frames = []
    time_variants = ['time', 'Time', 't', 'T']  # Common names for time variables

    for file_path in mat_files:
        # Load the .mat file
        data = scipy.io.loadmat(file_path)
        key = next(key for key in data if not key.startswith('__'))  # Find the first relevant key
        mat_data = data[key]

        # Check the orientation of the data and correct if needed
        if mat_data.shape[0] < mat_data.shape[1]:  # Data is a row vector
            mat_data = mat_data.T

        # Create a DataFrame assuming the first column is time and the rest are data
        df = pd.DataFrame(mat_data, columns=['Time'] + [f'{key}_{i}' for i in range(1, mat_data.shape[1])])
        data_frames.append(df)

    # Merge all data frames on the 'Time' column
    final_df = data_frames[0]
    for df in data_frames[1:]:
        final_df = pd.merge(final_df, df, on='Time', how='outer')

    # Sort by Time and fill missing values with forward fill method
    final_df = final_df.sort_values('Time').ffill()

    # Save to CSV
    final_df.to_csv(csv_filepath, index=False)
