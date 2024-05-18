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
    convert_seconds_list_to_times : Converts a value in seconds to a
                                    properly formatted string.
                                    Opposite of this function.

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


def convert_seconds_to_time_str(seconds: float) -> str:
    """
    Convert a time duration in seconds to a formatted time string.

    This function converts a given time duration in seconds to a
    string formatted as `MM:SS.mmm`, where `MM` is the number of
    minutes, `SS` is the number of seconds (zero-padded to two
    digits), and `mmm` is the fractional part of the seconds
    (zero-padded to three digits).

    Parameters
    ----------
    seconds : float
        The time duration in seconds to be converted.

    Returns
    -------
    str
        The formatted time string in `MM:SS.mmm` format.

    Examples
    --------
    >>> convert_seconds_to_time_str(125.678)
    '02:05.678'

    >>> convert_seconds_to_time_str(59.999)
    '00:59.999'

    >>> convert_seconds_to_time_str(3600.001)
    '60:00.001'

    >>> convert_seconds_to_time_str(0)
    '00:00.000'
    """
    minutes = int(seconds // 60)
    seconds_remainder = seconds % 60
    formatted_time = f"{minutes:02}:{seconds_remainder:06.3f}"
    return formatted_time


def convert_seconds_to_time_list(seconds_list: list[float]) -> list[str]:
    """
    Convert a list of time durations in seconds to a list of formatted
    time strings.

    This function takes a list of time durations in seconds and
    converts each duration to a string formatted as `MM:SS.mmm`, where
    `MM` is the number of minutes, `SS` is the number of seconds
    (zero-padded to two digits), and `mmm` is the fractional part of
    the seconds (zero-padded to three digits).

    Parameters
    ----------
    seconds_list : list of float
        A list of time durations in seconds to be converted.

    Returns
    -------
    list of str
        A list of formatted time strings in `MM:SS.mmm` format.

    See Also
    --------
    convert_seconds_to_time_str : Convert a single time value to a
                                  properly formatted time string.
    convert_time_list_to_seconds : Converts a value from a time string
                                   to the total amount of seconds.
                                   Opposite of this function.

    Examples
    --------
    >>> convert_seconds_to_time_list([125.678, 59.999, 3600.001, 0])
    ['02:05.678', '00:59.999', '60:00.001', '00:00.000']

    >>> convert_seconds_to_time_list([0.5, 90.123, 45.678])
    ['00:00.500', '01:30.123', '00:45.678']
    """
    return [convert_seconds_to_time_str(seconds) for seconds in seconds_list]
