"""
Map Plotting Functions
======================
"""

from enum import Enum
from typing import Optional
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pint

from race_analysis.column_names import COL_LATITUDE, COL_LONGITUDE
from race_analysis.df_utils import slice_into_df
from race_analysis.laps_data import get_lap_indices, get_usable_lap_nums
from race_analysis.plot_data import reset_plot, save_plot, save_or_show_plot
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
        The type of Google Maps layer to use.  Must be one of
        {'m', 's', 'p', 'y'}.  Default is 'm'.

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
            The type of Google Maps layer to use.  Must be one of
            {'m', 's', 'p', 'y'}.  Default is 'm'.
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
        tile_source: MapType = MapType.OSM,
        save_plots: bool = True,
        show_plots: bool = False,
        track_name: Optional[str] = None,
        set_custom_colors: Optional[dict[float, str]] = None,
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
        The map tile source to use.  Default is MapType.OSM.
    save_plot : bool, optional (default True)
        Boolean indicating whether or not the generated plot should be
        saved as a file.  If True, the plot will be saved.  If False,
        the plot will not be saved.  By default True.
    show_plot : bool, optional (default False)
        Boolean indicating whether or not the generated plot should be
        displayed while running.  If False, the plot will not be
        displayed.  If True, the plot will be displayed.  By default
        False.
    track_name : str, optional
        The name of the track being plotted.  If defined, the plot's
        saved filename will be prepended by the track name.
    set_custom_colors : dict[float, str], optional
        Optional dictionary mapping values in the dataset to specific
        colors that should be plotted for those specific values.  For
        example, ``{0: 'red'}`` would plot all 0 values as red.

    Returns
    -------
    None
        This function does not return any value.  It saves the plot to
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

    # Normalize the values for color mapping
    if set_custom_colors is not None:
        min_val = min(list(set_custom_colors.keys()), new_df[data_name].min())
        max_val = max(list(set_custom_colors.keys()), new_df[data_name].max())
    else:
        min_val = new_df[data_name].min()
        max_val = new_df[data_name].max()

    norm = plt.Normalize(vmin=min_val, vmax=max_val)
    cmap = plt.get_cmap('viridis')
    map_spacing = 0.001

    #### DETERMINE OPTIMAL FIGURE DIMENSIONS ####
    lon_min, lon_max = min(new_df[COL_LONGITUDE]) - map_spacing, max(new_df[COL_LONGITUDE]) + map_spacing
    lat_min, lat_max = min(new_df[COL_LATITUDE]) - map_spacing,  max(new_df[COL_LATITUDE]) + map_spacing

    max_size = 10

    # Calculate the aspect ratio of the map
    aspect_ratio = (lat_max - lat_min) / (lon_max - lon_min)

    if aspect_ratio >= 1:
        figsize = (max_size / aspect_ratio, max_size)
    else:
        figsize = (max_size, max_size * aspect_ratio)
    #############################################

    # Create a plot with an appropriate projection
    fig, ax = plt.subplots(figsize=figsize, dpi=300, subplot_kw={'projection': tile_source.value.crs})
    ax.set_extent([min(new_df[COL_LONGITUDE]) - map_spacing, max(new_df[COL_LONGITUDE]) + map_spacing, min(new_df[COL_LATITUDE]) - map_spacing, max(new_df[COL_LATITUDE]) + map_spacing], crs=ccrs.Geodetic())

    # Add the tile layer
    zoom_level = 21
    ax.add_image(tile_source.value, zoom_level)

    point_size = 10

    for _, row in new_df.iterrows():
        ax.plot(row[COL_LONGITUDE], row[COL_LATITUDE], color="white", marker='o', markersize=point_size+4, alpha=0.7, transform=ccrs.Geodetic())

    for _, row in new_df.iterrows():
        row_value = row[data_name]
        if set_custom_colors is not None and row_value in set_custom_colors:
            color = set_custom_colors[row_value]
        else:
            color = cmap(norm(row_value))
        ax.plot(row[COL_LONGITUDE], row[COL_LATITUDE], color=color, marker='o', markersize=point_size, alpha=0.7, transform=ccrs.Geodetic())

    # Custom colormap to handle values less than zero in red
    if set_custom_colors is not None:
        custom_colors = cmap(np.linspace(0, 1, cmap.N))
        for custom_value, value_color in set_custom_colors.items():
            custom_value_index = np.searchsorted(np.linspace(min_val, max_val, cmap.N), custom_value)
            ## MAKE ALL VALUES LESS THAN ZERO THE ZERO-COLOR
            custom_colors = np.vstack([[mcolors.to_rgba(value_color)] * custom_value_index + list(custom_colors[custom_value_index:])])
            ## INSERTS ZERO-COLOR AT CORRECT LOCATION
            # custom_colors = np.vstack([custom_colors[:custom_value_index], [mcolors.to_rgba(value_color)], custom_colors[custom_value_index:]])

        custom_cmap = mcolors.ListedColormap(custom_colors)
    else:
        custom_cmap = cmap

    # Create the colorbar
    colorbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=custom_cmap), ax=ax, orientation='vertical', label=colorbar_label, pad=0.02, aspect=15)
    colorbar.set_label(colorbar_label, labelpad=15, fontsize=14)
    colorbar.ax.tick_params(labelsize=12)

    plot_title = f'{data_name} - Lap {lap_num}'
    # plt.title(f'Vehicle {data_name} on {tile_source.name} - Lap {lap_num}')
    # fig.suptitle(plot_title, fontsize=16)
    plt.tight_layout()

    if save_plots:
        final_filename = f'{f"{track_name} - " if track_name is not None else ""}{plot_title}'
        save_plot(data_filepath, name=final_filename, lap_num=lap_num)
    if show_plots:
        plt.show()

    reset_plot()


def plot_map_every_lap(
        df: pd.DataFrame,
        data_to_plot: pd.Series,
        data_units: str | pint.Unit,
        colorbar_label: str,
        data_filepath: str,
        tile_source: MapType = MapType.OSM,
        usable_laps: Optional[list[int]] = None,
        save_plots: bool = True,
        show_plots: bool = False,
        track_name: Optional[str] = None,
        set_custom_colors: Optional[dict[float, str]] = None,
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
    tile_source : MapType, optional
        The map tile source to use.  Default is MapType.OSM.
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
    track_name : str, optional
        The name of the track being plotted.  If defined, the plot's
        saved filename will be prepended by the track name.
    set_custom_colors : dict[float, str], optional
        Optional dictionary mapping values in the dataset to specific
        colors that should be plotted for those specific values.  For
        example, ``{0: 'red'}`` would plot all 0 values as red.

    Returns
    -------
    None
        This function does not return any value.  It saves the plots
        to the specified file path and displays them.

    See Also
    --------
    plot_map : Plot a map with data points overlaid using specified
               map tiles.
    get_usable_laps : Function to get the usable lap numbers from the
                      DataFrame.
    MapType : Enum for different map types including Google Maps and
              OpenStreetMap.

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
            tile_source=tile_source,
            save_plots=save_plots,
            show_plots=show_plots,
            track_name=track_name,
            set_custom_colors=set_custom_colors,
        )
