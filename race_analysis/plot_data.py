import pandas as pd
import matplotlib.pyplot as plt

from utils import convert_to_magnitude

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
        y_label: str
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
