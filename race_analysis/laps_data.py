import pandas as pd
import numpy as np
from geopy.distance import great_circle
from sklearn.cluster import DBSCAN

from .utils import strip_df_of_units


def identify_starting_point(df: pd.DataFrame):
    """
    Identify the centroid of the most populated cluster in geographic
    data.

    This function uses DBSCAN clustering to group geographic
    coordinates and identifies the centroid of the most populated
    cluster, which might represent a significant location such as a
    start/finish line in a race.

    Parameters
    ----------
    df : pd.DataFrame
        A pandas DataFrame containing the columns 'GPS Latitude' and
        'GPS Longitude', representing geographical coordinates.

    Returns
    -------
    tuple
        A tuple representing the latitude and longitude of the
        centroid of the most populated cluster.

    Examples
    --------
    >>> data = {'GPS Latitude': [34.052235, 34.052235, 34.052235],
    ...         'GPS Longitude': [-118.243683, -118.243683, -118.243683]}
    >>> df = pd.DataFrame(data)
    >>> identify_starting_point(df)
    (34.052235, -118.243683)

    Notes
    -----
    - DBSCAN parameters: `eps` approximates to 50 meters (can be
      adjusted based on the specific dataset) and requires at least 10
      samples to form a cluster.
    - Ensure that the DataFrame does not include units in the
      coordinate columns and that they are appropriately named as 'GPS
      Latitude' and 'GPS Longitude'.
    """
    kms_per_radian = 6371.0088
    epsilon = 0.05 / kms_per_radian  # convert to radians for the haversine formula
    db = DBSCAN(eps=epsilon, min_samples=10, algorithm='ball_tree', metric='haversine').fit(
        np.radians(strip_df_of_units(df[['GPS Latitude', 'GPS Longitude']], rename_cols_with_units=False)))
    cluster_labels = db.labels_
    # Find the cluster that has the most points (most likely to be the start/finish line)
    largest_cluster = np.argmax(np.bincount(cluster_labels[cluster_labels >= 0]))
    
    # Compute the centroid of the largest cluster
    largest_cluster_indices = np.where(cluster_labels == largest_cluster)
    largest_cluster_points = df.iloc[largest_cluster_indices]
    centroid = (largest_cluster_points['GPS Latitude'].mean(), largest_cluster_points['GPS Longitude'].mean())
    return centroid


def find_laps(df: pd.DataFrame):
    minimal_df = strip_df_of_units(df[['dT', 'GPS Latitude', 'GPS Longitude']], rename_cols_with_units=False)
    # Identify the starting point (most visited point, likely to be the start/finish line)
    start_lat, start_lon = identify_starting_point(minimal_df)
    
    # Threshold for considering the car has passed the start/finish line (in kilometers)
    threshold = 0.05
    
    # Initialize lap counter and list to store the lap number for each point
    current_lap = 1
    current_lap_time = 0
    lap_numbers = []
    lap_times = []

    for index, row in minimal_df.iterrows():
        distance_from_start = great_circle((start_lat, start_lon), (row['GPS Latitude'], row['GPS Longitude'])).kilometers
        
        is_new_lap = (
            distance_from_start <= threshold and    # Ensure distance from starting point is reasonable
            index > 0 and                           # Avoid counting the first point if it's close to the start
            (
                current_lap_time >= 10 or           # Ensure the current lap is at least 10 seconds long
                current_lap == 1                    # Or skip this check if this is the first lap
            )
        )
        current_lap_time += row['dT']

        if is_new_lap:  # Avoid counting the first point if it's close to the start
            current_lap += 1
            current_lap_time = 0

        lap_numbers.append(current_lap)
        lap_times.append(current_lap_time)

    df['Lap Number'] = pd.Series(data=lap_numbers, name='Lap Number', dtype='pint[dimensionless]')
    df['Current Lap Time'] = pd.Series(data=lap_times, name='Lap Time', dtype='pint[second]')

    return df
