"""Global warming and wildfire intensity in California, USA
   Menu Option 6: Display wildfire occurrence map of given month and year
"""
from wildfire_read import get_years_wildfire
from temp_data import TEMP_DATA
import statistics
# Below are newly installed libraries used to draw the wildfire occurrence map
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd


FIRE_DATASET = get_years_wildfire(2007, 2015)   # read data of all fires in California from 2007 to 2015
TEMP_DATASET = TEMP_DATA  # read temperature data


def fire_data_by_month(year: int, month: str) -> dict:
    """Return a dictionary mapping fire properties to lists of the data of each fire in the given month and year.
    """

    fires = [fire for fire in FIRE_DATASET[year][month]]
    data = {'fire_size_value': [],
            'Latitude': [],
            'Longitude': [],
            'marker_color': []}

    for fire in fires:
        fire_size = fire[2]
        duration = (fire[1] - fire[0]).days + (fire[1] - fire[0]).seconds / (3600 * 24)
        location = fire[4]
        data['fire_size_value'].append(fire_size * duration)
        data['Latitude'].append(location[0])
        data['Longitude'].append(location[1])
        data['marker_color'].append(get_marker(fire_size * duration))

    return data


def get_marker(fire_data: int) -> float:
    """Return an int value of the marker size corresponding to the value of fire_data.
    """
    return (fire_data * 1000) ** (1/10)


def average_max_temp_month(year: int, month: str) -> float:
    """Return the average maximum temperature of a given month."""
    max_temp = [temp[1] for temp in TEMP_DATASET[year][month]]
    return statistics.mean(max_temp)


def plot(month: str, year: int) -> None:
    """Plot the wildfire map of California in the given month of given year.
    """

    df = pd.DataFrame(fire_data_by_month(year, month))  # store the fire data
    map = gpd.read_file('CA_counties.shp')  # read the shape file of California in project folder using geopandas
    fig, ax = plt.subplots(figsize=(8, 8))  # set the size of the figure to be drawn

    ax.xaxis.set_label_text('Longitude')  # label x axis
    ax.yaxis.set_label_text('Latitude')   # label y axis
    ax.set_title("Wildfires in California in "
                 + month + ", " + str(year)
                 + ", Average Max.Temp = "
                 + str(round(average_max_temp_month(year, month), 2)))  # add title of the figure

    # store fire location as data points on GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    # plot base map and fire data points
    map.plot(ax=ax, alpha=1, color='grey')  # set base map transparency to 1 and color to grey
    # set size of scatter points to 50, transparency to 0.85, and color to 'hot_r' color map
    gdf.plot(ax=ax, markersize=50, alpha=0.85, column=df.marker_color, cmap='hot_r', legend=True)

    plt.show()  # show the graph
