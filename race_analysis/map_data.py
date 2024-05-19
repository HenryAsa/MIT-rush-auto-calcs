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
from race_analysis.laps_data import get_lap_indices, get_usable_lap_nums
from race_analysis.plot_data import save_plot, save_or_show_plot
from race_analysis.utils import get_filename


class GoogleCustomTiles(cimgt.GoogleTiles):
    """
    Custom Google Maps tile provider with selectable layer type.

    This class provides Google Maps tiles with selectable layer
    types, which can be one of 'm' (map), 's' (satellite), 'p'
    (terrain), or 'y' (hybrid).

    Parameters
    ----------
    layer_type : str, optional
        The type of Google Maps layer to use. Must be one of
        {'m', 's', 'p', 'y'}. Default is 'm'.

    Notes
    -----
    Available layer types include `'m'` (map), `'s'` (satellite),
    `'p'` (terrain), and `'y'` hybrid.

    Examples
    --------
    >>> tiles = GoogleCustomTiles(layer_type='s')
    >>> url = tiles._image_url((1, 2, 3))
    >>> print(url)
    'https://mt.google.com/vt/lyrs=s&x=1&y=2&z=3'
    """

    def __init__(self, layer_type='m'):
        """
        Initialize GoogleCustomTiles with the specified layer type.

        Parameters
        ----------
        layer_type : str, optional
            The type of Google Maps layer to use. Must be one of
            {'m', 's', 'p', 'y'}. Default is 'm'.
        """
        assert layer_type in {'m', 's', 'p', 'y'}
        self.layer_type = layer_type
        super().__init__()

    def _image_url(self, tile):
        """
        Generate the URL for a Google Maps tile.

        Parameters
        ----------
        tile : tuple of int
            A tuple (x, y, z) representing the tile coordinates and
            zoom level.

        Returns
        -------
        url : str
            The URL for the specified Google Maps tile.

        Examples
        --------
        >>> tiles = GoogleCustomTiles(layer_type='y')
        >>> url = tiles._image_url((1, 2, 3))
        >>> print(url)
        'https://mt.google.com/vt/lyrs=y&x=1&y=2&z=3'
        """
        x, y, z = tile
        url = f"https://mt.google.com/vt/lyrs={self.layer_type}&x={x}&y={y}&z={z}"
        return url


class MapType(Enum):
    """
    Enum for different map types including Google Maps and
    OpenStreetMap.

    This enum defines various map types such as Google Maps with
    different layer types and OpenStreetMap.

    Attributes
    ----------
    GOOGLE_ROADMAP : GoogleCustomTiles
        Google Maps with road map layer.
    GOOGLE_SATELITE : GoogleCustomTiles
        Google Maps with satellite layer.
    GOOGLE_TERRAIN : GoogleCustomTiles
        Google Maps with terrain layer.
    GOOGLE_HYBRID : GoogleCustomTiles
        Google Maps with hybrid layer.
    GOOGLE_DEFAULT : cimgt.GoogleTiles
        Default Google Maps tiles.
    OSM : cimgt.OSM
        OpenStreetMap tiles.

    See Also
    --------
    GoogleCustomTiles : Custom Google Maps tile provider with
                        selectable layer type.
    cimgt.GoogleTiles : Default Google Maps tile provider from
                        Cartopy.
    cimgt.OSM : OpenStreetMap tile provider from Cartopy.

    Notes
    -----
    To access the actual MapType `cartopy.io.img_tiles` object, simply
    do `MapType.value` for some instance of a MapType.

    Examples
    --------
    >>> map_type = MapType.GOOGLE_ROADMAP
    >>> print(map_type)
    MapType GOOGLE_ROADMAP
    """
    GOOGLE_ROADMAP = GoogleCustomTiles(layer_type='m')
    GOOGLE_SATELITE = GoogleCustomTiles(layer_type='s')
    GOOGLE_TERRAIN = GoogleCustomTiles(layer_type='p')
    GOOGLE_HYBRID = GoogleCustomTiles(layer_type='y')
    GOOGLE_DEFAULT = cimgt.GoogleTiles()
    OSM = cimgt.OSM()

    def __str__(self):
        """
        Return the string representation of the MapType.

        Returns
        -------
        str
            The string representation of the MapType.

        Examples
        --------
        >>> map_type = MapType.OSM
        >>> str(map_type)
        'MapType OSM'
        """
        return f'MapType {self.name}'


def plot_map(
        df: pd.DataFrame,
        data_to_plot: pd.Series,
        data_units: str | pint.Unit,
        lap_num: int,
        colorbar_label: str,
        data_filepath: str,
        tile_source: Optional[MapType] = MapType.OSM,
        save_plots: bool = True,
        show_plots: bool = False,
    ) -> None:
    """
    Plot a map with data points overlaid using specified map tiles.

    This function plots a map with data points from a pandas
    DataFrame, overlaid on map tiles from various sources, for a
    specific lap number.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the latitude and longitude data.
    data_to_plot : pd.Series
        Series containing the data to be plotted.
    data_units : str or pint.Unit
        Units of the data to be plotted.
    lap_num : int
        Lap number for which the data should be plotted.
    colorbar_label : str
        Label for the colorbar indicating the data units.
    data_filepath : str
        File path to save the plot.
    tile_source : MapType, optional
        The map tile source to use. Default is MapType.OSM.
    save_plot : bool, optional (default True)
        Boolean indicating whether or not the generated plot should be
        saved as a file.  If True, the plot will be saved.  If False,
        the plot will not be saved.  By default True.
    show_plot : bool, optional (default False)
        Boolean indicating whether or not the generated plot should be
        displayed while running.  If False, the plot will not be
        displayed.  If True, the plot will be displayed.  By default
        False.

    Returns
    -------
    None
        This function does not return any value. It saves the plot to
        the specified file path and displays it.

    See Also
    --------
    MapType : Enum for different map types including Google Maps and
              OpenStreetMap.
    GoogleCustomTiles : Custom Google Maps tile provider with
                        selectable layer type.
    get_lap_indices : Function to get the start and end indices for
                      each lap.
    slice_into_df : Function to slice data into a DataFrame based on
                    indices.

    Notes
    -----
    This function uses the Cartopy library to create map plots with
    various map tile sources.  The `tile_source` parameter allows
    switching between different map types like Google Maps and
    OpenStreetMap.  The data to be plotted should have compatible
    units with the specified `data_units`.

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'Latitude': [34.0219, 34.0220, 34.0221],
    ...     'Longitude': [-118.4814, -118.4815, -118.4816],
    ...     'Speed': [10, 20, 30]
    ... })
    >>> data_to_plot = df['Speed']
    >>> plot_map(df, data_to_plot, 'meters/second', 0,
    ...          'Speed (m/s)', 'path/to/save/plot.png')
    """
    save_or_show_plot(save_plots=save_plots, show_plots=show_plots)

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
        zoom_level = 18
        ax.add_image(tile_source, zoom_level)

        for _, row in new_df.iterrows():
            color = cmap(norm(row[data_name]))
            ax.plot(row[COL_LONGITUDE], row[COL_LATITUDE], color=color, marker='o', markersize=10, alpha=0.7, transform=ccrs.Geodetic())

        plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, orientation='vertical', label=colorbar_label)
        plt.title(f'Vehicle {data_name} on {map.name} - Lap {lap_num}')
        plt.tight_layout()

        if save_plots:
            save_plot(data_filepath, name=f'{map.name} {ax.get_title()}', lap_num=lap_num)
        if show_plots:
            plt.show()

        plt.close()


def plot_map_every_lap(
        df: pd.DataFrame,
        data_to_plot: pd.Series,
        data_units: str | pint.Unit,
        colorbar_label: str,
        data_filepath: str,
        usable_laps: Optional[list[int]] = None,
        save_plots: bool = True,
        show_plots: bool = False,
    ) -> None:
    """
    Plot maps for each lap with data points overlaid using specified map tiles.

    This function plots maps with data points from a pandas DataFrame for
    each lap within the specified range, using the given map tiles.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the latitude and longitude data.
    data_to_plot : pd.Series
        Series containing the data to be plotted.
    data_units : str or pint.Unit
        Units of the data to be plotted.
    colorbar_label : str
        Label for the colorbar indicating the data units.
    data_filepath : str
        File path to save the plots.
    usable_laps : list[int], optional
        List of usable laps for which the data should be plotted.  If
        not provided, the default usable laps defined in
        `lap_times.json` will be used.  By default None.
    save_plots : bool, optional (default True)
        Boolean indicating whether or not the generated plot should be
        saved as a file.  If True, the plot will be saved.  If False,
        the plot will not be saved.  By default True.
    show_plots : bool, optional (default False)
        Boolean indicating whether or not the generated plot should be
        displayed while running.  If False, the plot will not be
        displayed.  If True, the plot will be displayed.  By default
        False.

    Returns
    -------
    None
        This function does not return any value. It saves the plots
        to the specified file path and displays them.

    See Also
    --------
    plot_map : Plot a map with data points overlaid using specified
               map tiles.
    get_usable_laps : Function to get the usable lap numbers from the
                      DataFrame.

    Notes
    -----
    This function iterates over the range of lap numbers and calls the
    `plot_map` function for each lap.  It uses the Cartopy library to
    create map plots with various map tile sources.

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'Latitude': [34.0219, 34.0220, 34.0221] * 3,
    ...     'Longitude': [-118.4814, -118.4815, -118.4816] * 3,
    ...     'Speed': [10, 20, 30, 15, 25, 35, 20, 30, 40]
    ... })
    >>> data_to_plot = df['Speed']
    >>> plot_map_every_lap(df, data_to_plot, 'meters/second',
    ...                    'Speed (m/s)', 'path/to/save/plot.png', 0, 2)
    """
    save_or_show_plot(save_plots=save_plots, show_plots=show_plots)

    if usable_laps is None:
        usable_laps = get_usable_lap_nums(
            dataset_filename=get_filename(data_filepath)
        )

    for lap_num in usable_laps:
        plot_map(
            df=df,
            data_to_plot=data_to_plot,
            data_units=data_units,
            lap_num=lap_num,
            colorbar_label=colorbar_label,
            data_filepath=data_filepath,
            save_plots=save_plots,
            show_plots=show_plots
        )
