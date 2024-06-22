"""
DataFrame Columns Definitions and Extensions
============================================

Includes functions for defining additional columns to the master
`race_data` DataFrame.
"""

from typing import Optional

import numpy as np
import pandas as pd
import pint

from .constants import MASS_VEHICLE
from .units import u, Q_


def set_df_column(
        df: pd.DataFrame,
        units_dict: dict[str, str],
        name: str,
        data: pd.DataFrame | pd.Series,
        column_units: Optional[str | pint.Unit] = None,
    ) -> None:
    """
    Adds a new column to a DataFrame and assigns units to it.

    This function updates a given DataFrame by adding a new column
    with the specified name and data.  It also updates a dictionary
    that keeps track of the units for each column in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to which the new column will be added.
    units_dict : dict of str
        A dictionary mapping column names to their respective units.
    name : str
        The name of the new column to be added to the DataFrame.
    data : pd.DataFrame or pd.Series
        The data to be added as the new column.  It can be a DataFrame
        or Series.
    column_units : str or pint.Unit, optional
        The units for the new column if any are defined.

    Returns
    -------
    None
        This function does not return anything.  It modifies the
        DataFrame and units dictionary in place.

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `name` that contains the computed `data` values.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'A': [1, 2, 3]})
    >>> units_dict = {'A': 'meters'}
    >>> set_df_column(df, units_dict, 'B', pd.Series([4, 5, 6]), 'seconds')
    >>> print(df)
       A  B
    0  1  4
    1  2  5
    2  3  6
    >>> print(units_dict)
    {'A': 'meters', 'B': 'seconds'}
    """
    # series_units = u(str(data.loc[5].units))
    # defined_units = u(str(column_units))

    # if (series_units != defined_units) or (data.pint.units != defined_units):
    #     raise Exception(f'UNITS DO NOT MATCH FOR {name}\n\tSERIES UNITS:\t{series_units}\n\tDEFINED UNITS:\t{defined_units}')
    data_units = data.pint.units if column_units is None else column_units

    df[name] = data.pint.to(data_units)
    units_dict[name] = str(data_units)


def set_delta(
        df: pd.DataFrame,
        units: dict[str, str],
        col_to_delta: str,
        delta_name: str,
    ) -> None:
    """
    Adds a delta column to a DataFrame representing the difference
    between consecutive rows of a specified column.

    This function computes the difference between consecutive rows of
    the specified column in the DataFrame and adds a new column with
    these delta values.  The units dictionary is updated to include the
    units for the new delta column, which are assumed to be the same
    as those for the original column.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to which the delta column will be added.
    units : dict of str to str
        A dictionary mapping column names to their respective units.
        This dictionary will be updated with the new delta column name
        and units.
    col_to_delta : str
        The name of the column for which the row differences will be
        calculated.
    delta_name : str
        The name of the new delta column to be added to the DataFrame.

    Returns
    -------
    None

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `delta_name` that contains the computed delta
    values.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'time': [1, 2, 3, 4],
    ...     'value': [10, 20, 30, 40]
    ... })
    >>> units = {'time': 'seconds', 'value': 'units'}
    >>> set_delta(df, units, 'value', 'delta_value')
    >>> print(df)
       time  value  delta_value
    0     1     10          0.0
    1     2     20         10.0
    2     3     30         10.0
    3     4     40         10.0
    >>> print(units)
    {'time': 'seconds', 'value': 'units', 'delta_value': 'units'}
    """
    data_units = units[col_to_delta]
    data = df[col_to_delta].diff().fillna(0)  # Calculate time difference between measurements
    set_df_column(df, units, delta_name, data, data_units)


def set_time_derivative(
        df: pd.DataFrame,
        units: dict[str, str],
        col_to_derive: str,
        derivative_name: str,
    ) -> None:
    """
    Compute the time derivative of a column and set it in the
    DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data.
    units : dict[str, str]
        Dictionary mapping column names to their units.
    col_to_derive : str
        The name of the column to compute the derivative for.
    derivative_name : str
        The name of the column to store the derivative in.

    Returns
    -------
    None
        This function modifies the DataFrame in place.

    Notes
    -----
    This function computes the time derivative of the specified
    column using the difference between consecutive rows and the
    time interval stored in the `'Delta Time'` column.  The resulting
    derivative is stored in a new column of the DataFrame with units
    derived from the input units.

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> from set_time_derivative import set_time_derivative
    >>> data = {
    ...     'value': [1, 2, 4, 7, 11],
    ...     'Delta Time': [1, 1, 1, 1, 1]
    ... }
    >>> df = pd.DataFrame(data)
    >>> units = {'value': 'm', 'Delta Time': 's'}
    >>> set_time_derivative(df, units, 'value', 'value_derivative')
    >>> df
       value  dT  value_derivative
    0      1   1               0.0
    1      2   1               1.0
    2      4   1               2.0
    3      7   1               3.0
    4     11   1               4.0
    """
    derivative = (df[col_to_derive].diff().fillna(0) / df['Delta Time'].replace(0, np.nan))  # Avoid division by zero
    set_df_column(df, units, derivative_name, derivative)


#########################################################
#### SETTING MATH CHANNEL COLUMNS FROM RACE STUDIO 3 ####
#########################################################

def set_Distance_on_GPS_Speed(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "Distance on GPS Speed" Math Channel

    Distance on GPS Speed.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'Distance on GPS Speed'` that contains the
    computed values.
    """
    label = 'Distance on GPS Speed'
    data_units = 'm'
    data = ((df['GPS Speed'].shift().fillna(0) * df['Delta Time'].shift().fillna(0)).cumsum()).pint.to(data_units)
    set_df_column(df, units, label, data, data_units)


def set_GPS_G_Sum(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "GPS G Sum" Math Channel

    Outputs the abs value of the sum of the inline and lateral
    acceleration channels values.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'GPS G Sum'` that contains the computed values.
    """
    label = 'GPS G Sum'
    data_units = 'gravity'
    data = ((df['GPS LonAcc']**2 + df['GPS LatAcc']**2)**(1/2)).pint.to(data_units)
    set_df_column(df, units, label, data, data_units)


def set_GPS_BRK_On(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "GPS BRK On" Math Channel

    Computes when the inline acceleration g's are less than -0.15g.
    The outputs are : 0 = Brakes are off, 1 = Brakes are on.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'GPS BRK On'` that contains the computed values.
    """
    label = 'GPS BRK On'
    data_units = 'dimensionless'
    data = pd.Series(np.where(df['GPS LonAcc'] < Q_(-0.15, 'gravity'), Q_(1, data_units), Q_(0, data_units)), dtype=f'pint[{data_units}]')
    set_df_column(df, units, label, data, data_units)


def set_GPS_TPS_On(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "GPS TPS On" Math Channel

    Computes when the inline acceleration g's are greater than 0.05g.
    The outputs are: 0 = Throttle is off, 1 = Throttle is on.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'GPS TPS On'` that contains the
    computed values.
    """
    label = 'GPS TPS On'
    data_units = 'dimensionless'
    data = pd.Series(np.where(df['GPS LonAcc'] > Q_(0.05, 'gravity'), Q_(1, data_units), Q_(0, data_units)), dtype=f'pint[{data_units}]')
    set_df_column(df, units, label, data, data_units)


def set_GPS_CRN_On(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "GPS CRN On" Math Channel

    Computes when the lateral acceleration is greater than 0.2g.  The
    outputs are: 0 = On a straight, 1 = In a corner.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'GPS CRN On'` that contains the computed values.
    """
    label = 'GPS CRN On'
    data_units = 'dimensionless'
    data = pd.Series(np.where(abs(df['GPS LatAcc']) > Q_(0.2, 'gravity'), Q_(1, data_units), Q_(0, data_units)), dtype=f'pint[{data_units}]')
    set_df_column(df, units, label, data, data_units)


def set_GPS_CST_On(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "GPS CST On" Math Channel

    Computes when the driver is not on the brakes, and not on the
    throttle, and not in a corner.  The outputs are: 0 = Not coasting,
    1 = Coasting.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'GPS CST On'` that contains the computed values.
    """
    label = 'GPS CST On'
    data_units = 'dimensionless'
    zero = Q_(0, data_units)
    data = pd.Series(np.where((df['GPS BRK On'] == zero) & (df['GPS TPS On'] == zero) & (df['GPS CRN On'] == zero), Q_(1, data_units), Q_(0, data_units)), dtype=f'pint[{data_units}]')
    set_df_column(df, units, label, data, data_units)

#########################################################


#############################################
#### SETTING CUSTOM COLUMNS FOR ANALYSIS ####
#############################################

def set_delta_time(df: pd.DataFrame, units: dict[str, str]) -> None:
    r"""Computes the difference in time between each row of the
    dataframe.  This is the dT "Delta t" for the dataset.

    This function calculates the change in time using the difference
    between 'Time' columns in the dataframe.  The dT values are added
    as a new column labeled 'Delta Time' in the dataframe.

    .. math::
        \Delta t = t_{i+1} - t_i

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'Delta Time'` that contains the computed time deltas.
    """
    label = 'Delta Time'
    set_delta(df, units, 'Time', label)


def set_acceleration(df: pd.DataFrame, units: dict[str, str]) -> None:
    r"""Computes the Acceleration of the vehicle based on the change
    in vehicle velocity from the 'GPS Speed' channel.

    This function calculates the acceleration using the first
    difference of the 'GPS Speed' and the time intervals ('Delta Time')
    between measurements.

    .. math::
        a = \frac{\Delta v}{\Delta t}

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'Acceleration'` that contains the computed
    acceleration values.
    """
    label = 'Acceleration'
    set_time_derivative(df, units, 'GPS Speed', label)


def set_vehicle_kinetic_energy(
        df: pd.DataFrame,
        units: dict[str, str],
        mass: float = MASS_VEHICLE,
    ) -> None:
    r"""Compute the Kinetic Energy of the vehicle

    The kinetic energy of the vehicle is determined, where the default
    mass of `MASS_VEHICLE` is used (which is derived from the average
    mass of a person and the mass of the vehicle).

    .. math::
        KE = \frac{1}{2}mv^2

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'Vehicle Kinetic Energy'` that contains the
    computed kinetic energy values.
    """
    label = 'Vehicle Kinetic Energy'
    data_units = 'joules'
    data = pd.Series(data=(0.5 * mass * df['GPS Speed']**2), dtype=f'pint[{data_units}]')
    set_df_column(df, units, label, data, data_units)


def set_delta_vehicle_kinetic_energy(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Determine the change (delta) in Vehicle Kinetic Energy.  This
    column is titled "Delta KE".

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'Delta KE'` that contains the computed values.
    """
    label = 'Delta KE'
    set_delta(df, units, 'Vehicle Kinetic Energy', label)


def set_vehicle_power(df: pd.DataFrame, units: dict[str, str]) -> None:
    r"""
    Computes the power of the vehicle by taking the time derivative
    of the vehicle's kinetic energy.

    The Power :math:`P` of the vehicle is computed as the time
    derivative of its kinetic energy :math:`KE`:

    .. math::
        P = \frac{d(KE)}{dt}

    This is implemented by calculating the change in kinetic energy
    over the change in time between consecutive data points in the
    dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Race data dataframe containing the kinetic energy values.
    units : dict[str, str]
        Units dictionary for the race data dataframe.

    Notes
    -----
    The function modifies the input dataframe `df` by adding a new
    column labeled `'Power'` that contains the computed power values.

    Examples
    --------
    >>> import pandas as pd
    >>> data = {'Time': [0, 1, 2, 3], 'Vehicle Kinetic Energy': [0, 10, 40, 90]}
    >>> df = pd.DataFrame(data)
    >>> units = {'Time': 's', 'Vehicle Kinetic Energy': 'J'}
    >>> set_vehicle_power(df, units)
    >>> print(df)
       Time  Vehicle Kinetic Energy  Power
    0     0                      0    NaN
    1     1                     10   10.0
    2     2                     40   30.0
    3     3                     90   50.0

    """
    label = 'Power - dKE'
    set_time_derivative(df, units, 'Vehicle Kinetic Energy', label)

    label = 'Power - mav'
    new_dataset = MASS_VEHICLE * df['GPS LonAcc'] * df['GPS Speed']
    set_df_column(df, units, label, new_dataset, 'watts')

#############################################


def initialize_rs3_channels(race_data: pd.DataFrame, units: dict[str, str]) -> None:
    """Initializes all of the Race Studio 3-defined Math Channels for
    the analysis and adds them as columns to the `race_data` Dataframe.

    Initializes only the Race Studio 3-defined Math Channels.

    Parameters
    ----------
    race_data : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe
    """
    set_delta_time(df=race_data, units=units)
    set_Distance_on_GPS_Speed(df=race_data, units=units)
    set_GPS_G_Sum(df=race_data, units=units)
    set_GPS_BRK_On(df=race_data, units=units)
    set_GPS_TPS_On(df=race_data, units=units)
    set_GPS_CRN_On(df=race_data, units=units)
    set_GPS_CST_On(df=race_data, units=units)


def initialize_custom_channels(race_data: pd.DataFrame, units: dict[str, str]) -> None:
    """Initializes all of the custom user-defined channels for the
    analysis and adds them as columns to the `race_data` Dataframe.

    Initializes only the custom user-defined channels.

    Parameters
    ----------
    race_data : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe
    """
    set_acceleration(df=race_data, units=units)
    set_vehicle_kinetic_energy(df=race_data, units=units, mass=MASS_VEHICLE)
    set_delta_vehicle_kinetic_energy(df=race_data, units=units)
    set_vehicle_power(df=race_data, units=units)


def initialize_channels(race_data: pd.DataFrame, units: dict[str, str]) -> None:
    """Initializes all of the channels for the analysis and adds them
    as columns to the `race_data` Dataframe.

    Initializes both Race Studio 3 Math Channels, as well as custom
    channels defined by the user.

    Parameters
    ----------
    race_data : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe
    """
    ## INITIALIZE RACE STUDIO 3 MATH CHANNELS
    initialize_rs3_channels(race_data=race_data, units=units)

    ## INITIALIZE CUSTOM CHANNELS
    initialize_custom_channels(race_data=race_data, units=units)
