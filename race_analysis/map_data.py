"""
Map Plotting Functions
======================
"""

from enum import Enum
from typing import Optional
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import matplotlib.pyplot as plt
import pandas as pd
import pint

from race_analysis.column_names import COL_LATITUDE, COL_LONGITUDE
from race_analysis.df_utils import slice_into_df
from race_analysis.laps_data import get_lap_indices, get_start_end_laps
from race_analysis.plot_data import save_plot


class GoogleSatTiles(cimgt.GoogleTiles):
    def __init__(self, layer_type='m'):
        self.layer_type = layer_type
        super().__init__()

    def _image_url(self, tile):
        x, y, z = tile
        url = f"https://mt.google.com/vt/lyrs={self.layer_type}&x={x}&y={y}&z={z}"
        return url


class MapType(Enum):
    GOOGLE_ROADMAP = GoogleSatTiles(layer_type='m')
    GOOGLE_SATELITE = GoogleSatTiles(layer_type='s')
    GOOGLE_TERRAIN = GoogleSatTiles(layer_type='p')
    GOOGLE_HYBRID = GoogleSatTiles(layer_type='y')
    GOOGLE_DEFAULT = cimgt.GoogleTiles()
    OSM = cimgt.OSM()

    def __str__(self):
        return f'MapType {self.name}'


def plot_map(
        df: pd.DataFrame,
        data_to_plot: pd.Series,
        data_units: str | pint.Unit,
        lap_num: int,
        colorbar_label: str,
        data_filepath: str,
        tile_source: Optional[MapType] = MapType.GOOGLE_ROADMAP,
    ) -> None:
    """
    Plots vehicle data on an OSM map for each lap.

    This function generates a map plot for each lap of the vehicle,
    displaying the specified data (e.g., speed) on an OpenStreetMap
    (OSM) map. The data is color-coded based on its value and a
    colorbar is included for reference.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the telemetry data, including latitude
        and longitude information.
    data_to_plot : pd.Series
        Series containing the data to be plotted (e.g., speed).
    data_units : str | pint.Unit
        Units of the data to be plotted.
    colorbar_label : str
        Label for the colorbar indicating the units of the data.

    Returns
    -------
    None
        This function does not return any value. It generates and
        displays a plot for each lap.
    """
    data_name = data_to_plot.name
    lap_indices = get_lap_indices(df)
    start_lap_index, end_lap_index = lap_indices[lap_num]

    # valid_lap_times = slice_into_df(df['Time'], start_lap_index, end_lap_index)
    # reset_lap_times = np.linspace(0, valid_lap_times.iloc[-1] - valid_lap_times.iloc[0], len(valid_lap_times))

    new_df = pd.DataFrame({
        COL_LATITUDE: slice_into_df(df[COL_LATITUDE], start_lap_index, end_lap_index).pint.m_as('degrees'),
        COL_LONGITUDE: slice_into_df(df[COL_LONGITUDE], start_lap_index, end_lap_index).pint.m_as('degrees'),
        data_name: slice_into_df(data_to_plot, start_lap_index, end_lap_index).pint.m_as(data_units),
    })

    # Normalize the speed values for color mapping
    norm = plt.Normalize(new_df[data_name].min(), new_df[data_name].max())
    cmap = plt.get_cmap('viridis')
    map_spacing = 0.001

    for map in MapType:
        tile_source = map.value

        # Create a plot with an appropriate projection
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': tile_source.crs})
        ax.set_extent([min(new_df[COL_LONGITUDE]) - map_spacing, max(new_df[COL_LONGITUDE]) + map_spacing, min(new_df[COL_LATITUDE]) - map_spacing, max(new_df[COL_LATITUDE]) + map_spacing], crs=ccrs.Geodetic())

        # Add the tile layer
        ax.add_image(tile_source, 18)  # The second argument is the zoom level

        for _, row in new_df.iterrows():
            color = cmap(norm(row[data_name]))
            ax.plot(row[COL_LONGITUDE], row[COL_LATITUDE], color=color, marker='o', markersize=10, alpha=0.7, transform=ccrs.Geodetic())

        plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, orientation='vertical', label=colorbar_label)
        plt.title(f'Vehicle {data_name} on {map.name} - Lap {lap_num}')
        save_plot(data_filepath, name=f'{tile_source} {ax.get_title()}', lap_num=lap_num)
        plt.show()


def plot_map_every_lap(
        df: pd.DataFrame,
        data_to_plot: pd.Series,
        data_units: str | pint.Unit,
        colorbar_label: str,
        data_filepath: str,
        start_lap_num: Optional[int] = None,
        end_lap_num: Optional[int] = None,
    ) -> None:
    """
    Plots vehicle data on an OSM map for each lap.

    This function generates a map plot for each lap of the vehicle,
    displaying the specified data (e.g., speed) on an OpenStreetMap
    (OSM) map. The data is color-coded based on its value and a
    colorbar is included for reference.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the telemetry data, including latitude
        and longitude information.
    data_to_plot : pd.Series
        Series containing the data to be plotted (e.g., speed).
    data_units : str | pint.Unit
        Units of the data to be plotted.
    colorbar_label : str
        Label for the colorbar indicating the units of the data.

    Returns
    -------
    None
        This function does not return any value. It generates and
        displays a plot for each lap.
    """
    default_start_lap_num, default_end_lap_num = get_start_end_laps(df)

    if start_lap_num is None:
        start_lap_num = default_start_lap_num
    if end_lap_num is None:
        end_lap_num = default_end_lap_num

    for lap_num in range(start_lap_num, end_lap_num + 1):
        plot_map(
            df=df,
            data_to_plot=data_to_plot,
            data_units=data_units,
            lap_num=lap_num,
            colorbar_label=colorbar_label,
            data_filepath=data_filepath,
        )
