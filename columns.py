import numpy as np
import pandas as pd
from units import u, Q_

def set_delta(
        df: pd.DataFrame,
        units: dict[str, str],
        col_to_delta: str,
        delta_name: str,
    ) -> None:
    units[delta_name] = units[col_to_delta]
    df[delta_name] = df[col_to_delta].diff().fillna(0)  # Calculate time difference between measurements



def set_dt(df: pd.DataFrame, units: dict[str, str]) -> None:
    set_delta(df, units, 'Time', 'dT')


def set_acceleration(df: pd.DataFrame, units: dict[str, str]) -> None:
    label = 'Acceleration'
    units[label] = 'm/(s^2)'
    df[label] = (df['GPS Speed'].diff().fillna(0) / df['dT'].replace(0, np.nan))  # Avoid division by zero


def set_Distance_on_GPS_Speed(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "Distance on GPS Speed" Math Channel

    Distance on GPS Speed.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe
    """
    label = 'Distance on GPS Speed'
    units[label] = 'm'
    df[label] = (df['GPS Speed'].shift().fillna(0) * df['dT'].shift().fillna(0)).cumsum()


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
    """
    label = 'GPS G Sum'
    units[label] = 'gravity'
    df[label] = (df['GPS LonAcc']**2 + df['GPS LatAcc']**2)**(1/2)


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
    """
    label = 'GPS BRK On'
    units[label] = 'dimensionless'
    df[label] = pd.Series(np.where(df['GPS LonAcc'] < Q_(-0.15, 'gravity'), Q_(1, units[label]), Q_(0, units[label])), dtype=f'pint[{units[label]}]')


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
    """
    label = 'GPS TPS On'
    units[label] = 'dimensionless'
    df[label] = pd.Series(np.where(df['GPS LonAcc'] > Q_(0.05, 'gravity'), Q_(1, units[label]), Q_(0, units[label])), dtype=f'pint[{units[label]}]')


def set_GPS_CRN_On(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "GPS CRN On" Math Channel

    Computes when the lateral acceleration is greater than 0.2g. The
    outputs are: 0 = On a straight, 1 = In a corner.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe
    """
    label = 'GPS CRN On'
    units[label] = 'dimensionless'
    df[label] = pd.Series(np.where(abs(df['GPS LatAcc']) > Q_(0.2, 'gravity'), Q_(1, units[label]), Q_(0, units[label])), dtype=f'pint[{units[label]}]')


def set_GPS_CST_On(df: pd.DataFrame, units: dict[str, str]) -> None:
    """Set "GPS CST On" Math Channel

    Computes when the driver is not on the brakes, and not on the
    throttle, and not in a corner. The outputs are: 0 = Not coasting,
    1 = Coasting.

    Parameters
    ----------
    df : pd.DataFrame
        Race Data Dataframe
    units : dict[str, str]
        Units dictionary for a race data dataframe
    """
    label = 'GPS CST On'
    units[label] = 'dimensionless'
    zero = Q_(0, units[label])
    df[label] = pd.Series(np.where((df['GPS BRK On'] == zero) & (df['GPS TPS On'] == zero) & (df['GPS CRN On'] == zero), Q_(1, units[label]), Q_(0, units[label])), dtype=f'pint[{units[label]}]')


def initialize_channels(race_data: pd.DataFrame, units: dict[str, str]) -> None:
    ## SET NEW COLUMNS
    set_dt(df=race_data, units=units)
    set_Distance_on_GPS_Speed(df=race_data, units=units)
    set_GPS_G_Sum(df=race_data, units=units)
    set_GPS_BRK_On(df=race_data, units=units)
    set_GPS_TPS_On(df=race_data, units=units)
    set_GPS_CRN_On(df=race_data, units=units)
    set_GPS_CST_On(df=race_data, units=units)

    set_acceleration(df=race_data, units=units)