"""
Time Utility Functions
======================

This module provides utility functions for handling time-based data.
It includes functions that deal with converting time strings
formatted as 'MM:SS.sss' into total seconds as floating-point numbers.
"""


def convert_time_str_to_seconds(time_str: str) -> float:
    """
    Convert a time string in 'MM:SS.sss' format to total seconds.

    This function takes a time string formatted as 'MM:SS.sss' and
    converts it into the total number of seconds as a floating-point
    number.

    Parameters
    ----------
    time_str : str
        Time string in the format 'MM:SS.sss'.

    Returns
    -------
    float
        Total time in seconds.

    Examples
    --------
    >>> convert_time_str_to_seconds("02:30.500")
    150.5

    >>> convert_time_str_to_seconds("00:45.123")
    45.123

    >>> convert_time_str_to_seconds("10:00.000")
    600.0
    """
    minute, rest = time_str.split(':')
    seconds, milliseconds = rest.split('.')

    minute = int(minute)
    seconds = int(seconds)
    milliseconds = float(milliseconds) / 1000

    total_seconds = minute * 60 + seconds + milliseconds

    return total_seconds


def convert_time_list_to_seconds(time_list: list[str]) -> list[float]:
    """
    Convert a list of time strings in 'MM:SS.sss' format to total
    seconds.

    This function takes a list of time strings formatted as
    'MM:SS.sss' and converts each one into the total number of seconds
    as floating-point numbers.

    Parameters
    ----------
    time_list : list of str
        List of time strings in the format 'MM:SS.sss'.

    Returns
    -------
    list of float
        List of total times in seconds.

    See Also
    --------
    convert_time_str_to_seconds : Convert a single time string to
                                  total seconds.

    Examples
    --------
    >>> convert_time_list_to_seconds(["02:30.500", "00:45.123", "10:00.000"])
    [150.5, 45.123, 600.0]

    >>> convert_time_list_to_seconds(["00:01.000", "00:02.500", "00:03.750"])
    [1.0, 2.5, 3.75]

    >>> convert_time_list_to_seconds([])
    []
    """
    return [convert_time_str_to_seconds(time_str) for time_str in time_list]
