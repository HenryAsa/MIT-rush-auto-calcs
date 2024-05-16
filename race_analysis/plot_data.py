import matplotlib.pyplot as plt
import os
import pandas as pd
from typing import Optional

from .constants import PLOTS_DIRECTORY
from .utils import convert_to_magnitude, get_filename, get_folder_from_filepath

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
    x_data = convert_to_magnitude(race_data[x_series], units[x_series])
    y_data = convert_to_magnitude(race_data[y_series], units[y_series])
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
    or Series, and labels for the x and y axes. It then plots the data
    using matplotlib's plt.plot function and labels the axes
    accordingly.

    Parameters
    ----------
    x_data : pd.DataFrame | pd.Series
        Data for the x-axis. Must be a pandas DataFrame or Series.
    x_label : str
        Label for the x-axis.
    y_data : pd.DataFrame | pd.Series
        Data for the y-axis. Must be a pandas DataFrame or Series.
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
    # plt.show()


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
        The name of the file to save the plot as. If not provided, the
        plot title is used.
    lap_num : float, optional
        The lap number to include in the directory path. If not
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
    ax = plt.gca()

    if name is None:    name = ax.get_title()
    lap_folder = f'Lap {lap_num}/' if lap_num is not None else ''

    filepath = f'{PLOTS_DIRECTORY}/{get_filename(data_file).removesuffix(".csv")}/{lap_folder}{name}.pdf'
    os.makedirs(get_folder_from_filepath(filepath), exist_ok=True)

    plt.savefig(filepath)
