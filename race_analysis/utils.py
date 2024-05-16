import os
import pandas as pd
import pint

def convert_to_magnitude(data: pd.DataFrame | pd.Series, units: str) -> pd.DataFrame | pd.Series:
    return data.apply(lambda val: val.to(units).value)


def magnitude_of_df_col(column_name: str, df: pd.DataFrame, units: dict[str, str]) -> pd.DataFrame | pd.Series:
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
    Series. The renaming can be controlled by the
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
        else:
            new_df: pd.DataFrame = data_df.copy().pint.dequantify()
            new_df.columns = [col[0] for col in new_df.columns.values]
            return new_df

    elif isinstance(data_df, pd.Series):
        if rename_cols_with_units is True:
            name = f'{data_df.name} ({data_df.pint.to_base_units().pint.units})'
        else:
            name = data_df.name

        return pd.Series(name=name, data=data_df.copy().pint.to_base_units().pint.magnitude)

    raise incorrect_type_error


def get_files_with_extension(directory: str, extension: str) -> list[str]:
    """
    Get all files with the specified extension in the given directory.

    This function searches recursively through the directory and all
    subdirectories.  It collects paths to files that end with the
    given file extension.

    Parameters
    ----------
    directory : str
        The path of the directory to search in.
    extension : str
        The file extension to look for. It should start with a dot
        (e.g., '.txt').

    Returns
    -------
    list of str
        A list of full paths to files that have the specified extension.

    Examples
    --------
    >>> files = get_files_with_extension('/path/to/directory', '.txt')
    >>> print(files)
    ['/path/to/directory/file1.txt', '/path/to/directory/subdir/file2.txt']
    """
    # Normalize the extension to ensure it starts with a dot
    if not extension.startswith('.'):
        extension = '.' + extension

    # List to hold file paths
    files_with_extension = []

    # Walk through the directory
    for dirpath, dirnames, filenames in os.walk(directory):
        # Filter files by the specified extension
        for filename in filenames:
            if filename.endswith(extension):
                # Append the full path of the file
                files_with_extension.append(os.path.join(dirpath, filename))

    return files_with_extension


def get_folder_from_filepath(filepath: str) -> str:
    """
    Get the folder path from a given file path.

    This function extracts the directory portion of the provided file
    path, effectively removing the file name and returning the path to
    the directory containing the file.

    Parameters
    ----------
    filepath : str
        The full path to a file.

    Returns
    -------
    str
        The path to the directory containing the file.

    Examples
    --------
    >>> get_folder_from_filepath('/home/user/file.txt')
    '/home/user'

    >>> get_folder_from_filepath('C:\\Users\\file.txt')
    'C:\\Users'

    """
    return os.path.dirname(filepath)


def get_filename(filepath: str) -> str:
    """
    Retrieve the base name of the file from a given filepath.

    This function takes a full file path and returns only the
    file name, excluding the directory path.

    Parameters
    ----------
    filepath : str
        The full path to the file.

    Returns
    -------
    str
        The base name of the file.

    Examples
    --------
    >>> get_filename('/home/user/documents/file.txt')
    'file.txt'

    >>> get_filename('C:\\Users\\Documents\\file.txt')
    'file.txt'
    """
    return os.path.basename(filepath)
