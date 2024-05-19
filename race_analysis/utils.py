"""
General Utility Functions
=========================

A collection of utility functions for file and directory operations.

This module provides various functions to handle common tasks such as
retrieving files with specific extensions, extracting folder paths
from file paths, and getting file names from full paths.  These
functions are useful for file system navigation and manipulation.
"""

import os
from typing import Iterable, Optional

from race_analysis.constants import DATA_DIRECTORY


def get_data_files(data_directory: Optional[str] = DATA_DIRECTORY):
    """
    Retrieve all CSV files from the specified data directory.

    This function searches the specified data directory for all files
    with a '.csv' extension and returns them as a list.  By default,
    the `"data/formatted"` directory is referenced.

    Parameters
    ----------
    data_directory : str, optional
        The directory to search for CSV files. If not provided,
        defaults to `DATA_DIRECTORY`.

    Returns
    -------
    list of str
        A list containing the file paths of all CSV files in the
        specified data directory.

    See Also
    --------
    DATA_DIRECTORY : str
        Directory containing all of the parseable data.

    Examples
    --------
    >>> csv_files = get_data_files()
    >>> print(csv_files)
    ['/path/to/data/file1.csv', '/path/to/data/file2.csv']

    >>> csv_files = get_data_files('custom_directory')
    >>> print(csv_files)
    ['custom_directory/file1.csv', 'custom_directory/file2.csv']
    """
    return get_files_with_extension(data_directory, '.csv')


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
        The file extension to look for.  It should start with a dot
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


def filter_dict_keeping_specified_keys(
        dict_to_filter: dict,
        keys_to_keep: Iterable,
    ) -> dict:
    """
    Filter a dictionary to keep only specified keys.  Does not mutate
    the original dictionary, and instead returns a new dictionary.

    This function filters a given dictionary, including nested
    dictionaries, to retain only the keys specified in the
    `keys_to_keep` iterable.

    Parameters
    ----------
    dict_to_filter : dict
        The dictionary to be filtered.
    keys_to_keep : Iterable
        An iterable containing the keys to be retained in the
        dictionary.

    Returns
    -------
    dict
        A dictionary containing only the specified keys from the
        original dictionary, preserving the structure of nested
        dictionaries.

    Notes
    -----
    This function does not mutate the original dictionary.  It creates
    and returns a new dictionary containing only the specified keys.

    Examples
    --------
    Basic usage:

    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> keys = ['a', 'c']
    >>> filter_dict_keeping_specified_keys(d, keys)
    {'a': 1, 'c': 3}

    Nested dictionaries:

    >>> d = {'a': 1, 'b': {'ba': 21, 'bb': 22}, 'c': 3}
    >>> keys = ['a', 'b', 'ba']
    >>> filter_dict_keeping_specified_keys(d, keys)
    {'a': 1, 'b': {'ba': 21}}

    Filtering with no keys retained:

    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> keys = []
    >>> filter_dict_keeping_specified_keys(d, keys)
    {}
    """
    keys_to_keep = set(keys_to_keep)

    def filter_dict(dict_to_filter):
        if isinstance(dict_to_filter, dict):
            return {
                key: filter_dict(value)
                for key, value in dict_to_filter.items()
                if key in keys_to_keep
            }
        return dict_to_filter

    return {
        key: filter_dict(value)
        for key, value in dict_to_filter.items()
        if key in keys_to_keep
    }


def filter_dict_removing_specified_keys(
        dict_to_filter: dict,
        keys_to_delete: Iterable
    ) -> dict:
    """
    Filter a dictionary to remove specified keys.  Does not mutate the
    original dictionary, and instead returns a new dictionary.

    This function filters a given dictionary, including nested
    dictionaries, to remove the keys specified in the `keys_to_delete`
    iterable.

    Parameters
    ----------
    dict_to_filter : dict
        The dictionary to be filtered.
    keys_to_delete : Iterable
        An iterable containing the keys to be removed from the
        dictionary.

    Returns
    -------
    dict
        A dictionary excluding the specified keys from the original
        dictionary, preserving the structure of nested dictionaries.

    Notes
    -----
    This function does not mutate the original dictionary.  It creates
    and returns a new dictionary excluding the specified keys.

    Examples
    --------
    Basic usage:

    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> keys = ['b']
    >>> filter_dict_removing_specified_keys(d, keys)
    {'a': 1, 'c': 3}

    Nested dictionaries:

    >>> d = {'a': 1, 'b': {'ba': 21, 'bb': 22}, 'c': 3}
    >>> keys = ['b', 'bb']
    >>> filter_dict_removing_specified_keys(d, keys)
    {'a': 1, 'b': {'ba': 21}, 'c': 3}

    Filtering with all keys deleted:

    >>> d = {'a': 1, 'b': 2, 'c': 3}
    >>> keys = ['a', 'b', 'c']
    >>> filter_dict_removing_specified_keys(d, keys)
    {}
    """
    keys_to_delete = set(keys_to_delete)

    def filter_dict(dict_to_filter):
        if isinstance(dict_to_filter, dict):
            return {
                key: filter_dict(value)
                for key, value in dict_to_filter.items()
                if key not in keys_to_delete
            }
        return dict_to_filter

    return {
        key: filter_dict(value)
        for key, value in dict_to_filter.items()
        if key not in keys_to_delete
    }
