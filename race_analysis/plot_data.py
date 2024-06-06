"""
Generic Plotting Functions
==========================

Functions and methods designed to streamline plotting data.
"""

import os
from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd

from .constants import PLOTS_DIRECTORY
from .df_utils import convert_series_to_magnitude
from .utils import get_filename, get_folder_from_filepath


def plot_race_data(
        race_data: pd.DataFrame,
        units: dict[str, str],
        x_series: str,
        y_series: str,
    ) -> None:
    """Given the master RACE_DATA dataframe, this function plots the
    data given an x_column name of the dataframe and a y_column name
    of the dataframe.

    Parameters
    ----------
    race_data : pd.DataFrame
        Master dataframe to get x- and y-values from, where `x_series`
        and `y_series` are column keys of the dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe
    x_series : str
        Name of the column/key to use for the x-values of the plot
    y_series : str
        Name of the column/key to use for the y-values of the plot
    """
    x_data = convert_series_to_magnitude(race_data[x_series], units[x_series])
    y_data = convert_series_to_magnitude(race_data[y_series], units[y_series])
    plot_data(x_data, f'{x_series} ({units[x_series]})', y_data, f'{y_series} ({units[y_series]})')


def plot_data(
        x_data: pd.DataFrame | pd.Series,
        x_label: str,
        y_data: pd.DataFrame | pd.Series,
        y_label: str,
    ) -> None:
    """
    Plot data from pandas DataFrame or Series.

    This function takes x and y data in the form of pandas DataFrame
    or Series, and labels for the x and y axes.  It then plots the data
    using matplotlib's plt.plot function and labels the axes
    accordingly.

    Parameters
    ----------
    x_data : pd.DataFrame | pd.Series
        Data for the x-axis.  Must be a pandas DataFrame or Series.
    x_label : str
        Label for the x-axis.
    y_data : pd.DataFrame | pd.Series
        Data for the y-axis.  Must be a pandas DataFrame or Series.
    y_label : str
        Label for the y-axis.

    Examples
    --------
    >>> import pandas as pd
    >>> x = pd.Series([1, 2, 3, 4])
    >>> y = pd.Series([1, 4, 9, 16])
    >>> plot_data(x, 'Time', y, 'Distance')
    """
    plt.plot(x_data, y_data)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.tight_layout()


def save_plot(
        data_file: str,
        name: Optional[str] = None,
        lap_num: Optional[float] = None,
    ) -> None:
    """
    Save a plot to a specified directory as a PDF file.

    This function generates a plot and saves it as a PDF file in a
    directory derived from the `data_file` name.  The plot title or a
    provided name can be used as the filename.  An optional lap number
    can be included in the directory path.

    Parameters
    ----------
    data_file : str
        The path to the data file used to determine the save location.
    name : str, optional
        The name of the file to save the plot as.  If not provided, the
        plot title is used.
    lap_num : float, optional
        The lap number to include in the directory path.  If not
        provided, no lap folder is created.

    Returns
    -------
    None
        This function does not return any value.

    Examples
    --------
    Save a plot with default name and no lap number:
    >>> save_plot('data/session1.csv')

    Save a plot with a custom name:
    >>> save_plot('data/session1.csv', name='custom_plot')

    Save a plot with a lap number:
    >>> save_plot('data/session1.csv', lap_num=1.0)
    """

    if name is None:
        ax = plt.gca()
        name = ax.get_title()

    if name == "":
        fig = plt.gcf()
        name = fig._suptitle.get_text()

    lap_folder = f'Lap {lap_num}/' if lap_num is not None else ''

    filepath = f'{PLOTS_DIRECTORY}/{get_filename(data_file).removesuffix(".csv")}/{lap_folder}{name}.pdf'
    os.makedirs(get_folder_from_filepath(filepath), exist_ok=True)

    plt.savefig(filepath, bbox_inches='tight')


def save_or_show_plot(
        save_plots: bool,
        show_plots: bool,
    ) -> None:
    """
    Ensure that either saving or showing plots is enabled.

    This function checks that at least one of the `save_plots` or
    `show_plots` options is set to True.  If both are False, it
    raises a ValueError to prevent unnecessary computation.

    Parameters
    ----------
    save_plots : bool
        If True, plots will be saved to files.
    show_plots : bool
        If True, plots will be displayed.

    Raises
    ------
    ValueError
        If both `save_plots` and `show_plots` are False, indicating
        that no operation will be performed.

    Notes
    -----
    This function helps prevent wasting computational resources.  If
    neither saving nor showing plots is required, running the
    computation is redundant/pointless.  By ensuring at least one
    option is enabled, this function helps maintain efficient use of
    resources.

    Examples
    --------
    Ensure at least one of the options is enabled:

    >>> save_or_show_plot(True, False)
    # This will pass without any error.

    >>> save_or_show_plot(False, True)
    # This will pass without any error.

    >>> save_or_show_plot(True, True)
    # This will pass without any error.

    Raise an error if both options are disabled:

    >>> save_or_show_plot(False, False)
    Traceback (most recent call last):
        ...
    ValueError: This function effectively does nothing since both
    `save_plots` and `show_plots` are set to False.  At least one of
    these options must be True.
    """
    if not save_plots and not show_plots:
        raise ValueError('This function effectively does nothing since both `save_plots` and `show_plots` are set to False.  At least one of these options must be True.')


def reset_plot() -> None:
    """
    Reset the current Matplotlib plot.

    This function clears the current plot's axes, clears the current
    figure, and closes the figure window.  It is useful for ensuring
    that no residual plot data or settings affect subsequent plots.

    Notes
    -----
    This function is intended to be used in a workflow where multiple
    plots are generated in succession, and it is necessary to start
    each plot from a clean slate.

    Examples
    --------
    Resetting a plot before creating a new one:

    >>> import matplotlib.pyplot as plt
    >>> plt.plot([1, 2, 3], [4, 5, 6])
    >>> reset_plot()
    >>> plt.plot([7, 8, 9], [10, 11, 12])
    >>> plt.show()

    Using in a loop to create multiple independent plots:

    >>> for i in range(3):
    ...     plt.plot([1, 2, 3], [i, i+1, i+2])
    ...     plt.show()
    ...     reset_plot()
    """
    plt.cla()
    plt.clf()
    plt.close()
