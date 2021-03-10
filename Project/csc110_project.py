import datetime
from typing import Set, List, Dict, Tuple
import statistics
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from wildfire_read import get_years_wildfire
from temp_data import TEMP_DATA



EXAMPLE_TEMP_DATASET = TEMP_DATA

EXAMPLE_FIRE_DATASET = get_years_wildfire(2007, 2015)


# Dict[int: Dict[str: Tuple[Tuple[datetime.datetime, datetime.datetime, int, str, Tuple[int, int]]]]]
# Dict[year: Dict[month: Tuple[Tuple[start_time, end_time, fire_size, fire_class, Tuple[latitude, longitude]]]]

# Use these if needed.
def fire_intensity(year: int, month: str, start_time: datetime.datetime, end_time: datetime.time) -> float:
    """Return the fire_intensity of a given fire.

    The fire intensity is calculated based on the product of fire size and the duration of the fire"""
    fire = [fire for fire in EXAMPLE_FIRE_DATASET[year][month] if fire[0] == start_time and fire[1] == end_time][0]
    fire_size = fire[2]
    duration = (fire[1] - fire[0]).days + (fire[1] - fire[0]).seconds / (3600 * 24)

    return fire_size * duration


def fire_location(year: int, month: str, start_time: datetime.datetime, end_time: datetime.time) -> Tuple[float, float]:
    """Return the location of where the fire occurred.

    The location is a tuple of latitude and longitude e.g. (latitude,longitude)"""
    fire = [fire for fire in EXAMPLE_FIRE_DATASET[year][month] if fire[0] == start_time and fire[1] == end_time][0]
    return fire[4]


# Algorithms for plotly and pygame

# functions used to generate linear regression graph
# 9 possible combinations to implement the linear regression graph and see the correlation by month
# - Variable one: average, max, min temp
# - Variable two: average, max, min fire intensity
def average_max_temp_month(year: int, month: str) -> float:
    """Return the average maximum temperature of a given month."""
    max_temp = [temp[1] for temp in EXAMPLE_TEMP_DATASET[year][month]]
    return statistics.mean(max_temp)


def average_min_temp_month(year: int, month: str) -> float:
    """Return the average maximum temperature of a given month."""
    min_temp = [temp[2] for temp in EXAMPLE_TEMP_DATASET[year][month]]
    return statistics.mean(min_temp)


def average_temp_month(year: int, month: str) -> float:
    """Return the average of everyday average temperature of a given month."""
    return statistics.mean({average_max_temp_month(year, month), average_min_temp_month(year, month)})


def fire_average_intensity_by_month(year: int, month: str) -> float:
    """Return the average fire intensity of all fires in a given month"""
    return statistics.mean(fire_intensity_by_month(year, month))


def fire_max_intensity_by_month(year: int, month: str) -> float:
    """Return the average fire intensity of all fires in a given month"""
    return max(fire_intensity_by_month(year, month))


def fire_min_intensity_by_month(year: int, month: str) -> float:
    """Return the average fire intensity of all fires in a given month"""
    return min(fire_intensity_by_month(year, month))


# helper the functions of the above
def fire_intensity_by_month(year: int, month: str) -> List[float]:
    """Return the fire_intensity of all fires in a given month."""
    fires = [fire for fire in EXAMPLE_FIRE_DATASET[year][month]]

    accumulator = []
    for fire in fires:
        fire_size = fire[2]
        duration = (fire[1] - fire[0]).days + (fire[1] - fire[0]).seconds / (3600 * 24)
        accumulator.append(fire_size * duration)

    return accumulator


def create_regression_data(temp_data) -> List[Tuple[float, float]]:
    """Return a list of tuple that can be used to implement plotly graph."""
    accumulator = []
    for year in temp_data:
        for month in temp_data[year]:
            # change these two functions with different variables if needed
            accumulator.append((average_temp_month(year, month), fire_max_intensity_by_month(year, month)))

    return accumulator


#from here, borrowed from a1_part4
def generate_coordinates() -> tuple:
    """Return a tuple of two lists, containing the x- and y-coordinates of the given points.

    You may ASSUME that:
        - points is a list of tuples, where each tuple is a list of floats.

    """
    x_axis_dates = [datetime.date(year, month, 1)
                     for year in EXAMPLE_TEMP_DATASET.keys()
                     for month in range(1, 13)] # x axis is datetime variable, year and month and 1
    y_temperature = [average_temp_month(a, b)
                     for a in EXAMPLE_TEMP_DATASET.keys()
                     for b in EXAMPLE_TEMP_DATASET[a].keys()] # y axis is monthly temperature
    y_fire_intensity = [fire_average_intensity_by_month(year, month)
                        for year in EXAMPLE_FIRE_DATASET.keys()
                        for month in EXAMPLE_FIRE_DATASET[year].keys()]
    return (x_axis_dates, y_temperature, y_fire_intensity)


def linear_regression(points: list) -> tuple:
    """Perform a linear regression on the given points.

    points is a list of pairs of floats: [(x_1, y_1), (x_2, y_2), ...]
    This function returns a pair of floats (a, b) such that the line
    y = a + bx is the approximation of this data.

    Further reading: https://en.wikipedia.org/wiki/Simple_linear_regression

    You may ASSUME that:
        - len(points) > 0
        - each element of points is a tuple of two floats
    """
    x_coordinates = [points[i][0] for i in range(0, len(points))]
    y_coordinates = [points[i][1] for i in range(0, len(points))]

    b_part1 = sum([(x_coordinates[z] - average(x_coordinates))
                   * (y_coordinates[z] - average(y_coordinates))
                   for z in range(0, len(x_coordinates))])

    b_part2 = sum([(x_coordinates[z] - average(x_coordinates)) ** 2
                   for z in range(0, len(x_coordinates))])

    b = b_part1 / b_part2
    a = average(y_coordinates) - b * average(x_coordinates)
    return (a, b)


def average(values: list) -> float:
    """Return the average of values in a list of floats.

    >>> average([1.0, 2.0, 3.0, 4.0])
    2.5
    """
    return sum(values) / len(values)


def calculate_r_squared(points: list, a: float, b: float) -> float:
    """Return the R squared value when the given points are modelled as the line y = a + bx.

    points is a list of pairs of numbers: [(x_1, y_1), (x_2, y_2), ...]

    Assume that:
        - points is not empty and contains tuples
        - each element of points is a tuple containing two floats

    Further reading: https://en.wikipedia.org/wiki/Coefficient_of_determination
    """
    x_coordinates = [points[i][0] for i in range(0, len(points))]
    y_coordinates = [points[i][1] for i in range(0, len(points))]

    s_tot = sum([(y_coordinates[z] - average(y_coordinates)) ** 2
                 for z in range(len(y_coordinates))])

    s_res = sum([(y_coordinates[z] - (a + b * x_coordinates[z])) ** 2
                 for z in range(len(y_coordinates))])

    return 1 - (s_res / s_tot)


def run_example() -> tuple:
    """Run an example use of the functions in this file.

    Follow these example steps :
      1. Generates some random data points.
      2. Converts the points into the format expected by plotly.
      3. Performs a simple linear regression on the points.
      4. Plots the points and the line based on the regression using plotly.
      5. Calculates the R squared value for the regression model with this data.
      6. Returns the linear regression model and the R squared value.
    """
    points = create_regression_data(EXAMPLE_TEMP_DATASET)

    separated_coordinates = generate_coordinates()
    year = separated_coordinates[0]
    temperature = separated_coordinates[1]
    intensity = separated_coordinates[2]

    # Do a simple linear regression. Returns the (a, b) constants for
    # the line y = a + b * x.

    # temperature and fire intensity regression
    model = linear_regression(points)
    a = model[0]
    b = model[1]

    # Plot all the data points that have been randomly generated
    # plot_points(x_coords, y_coords)

    # Plot all the data points AND a line based on the regression
    plot_points_and_regression(year, temperature, intensity,  a, b, 100)

    # Calculate the r_squared value
    r_squared = calculate_r_squared(points, a, b)

    return (a, b, r_squared)


def plot_points() -> None:
    """Plot the given x- and y-coordinates using plotly. Display results in a web browser.

    x_coords is a list of floats representing the x-coordinates of the points,
    and y_coords is a list of float representing the y-coordinates of the points.
    These two lists must have the same length.

    We've provided this function for you, and you should not modify it!
    """
    # Create a blank figure
    points = generate_coordinates()
    x = points[0]
    y = points[1]
    scatter = go.Scatter(x=x, y=y)
    #layout = go.Layout(xaxis={'type': 'date'}) #, 'dtick': 86400000.0 * 30

    fig = go.Figure(data=[scatter])# , layout=layout

    # Add the raw data
    #fig.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='markers', name='Data'))

    # Display the figure in a web browser.
    fig.show()


def plot_points_and_regression(year: list, temperature: list, intensity: list,
                               a: float, b: float, x_max: float) -> None:
    """Plot the given x- and y-coordinates and linear regression model using plotly.

    The linear regression model is the line y = a + bx.
    Like plot_points, this function displays the results in a web browser.

    Note: this function calls your evaluate_line function, so make sure that you've
    tested your evaluate_line function carefully before try to call this one.

    We've provided this function for you, and you should not modify it!
    """
    fig = make_subplots(rows=3, cols=1)
    fig.append_trace(go.Scatter(x=year, y=temperature,), row=1, col=1)
    fig.append_trace(go.Scatter(x=year, y=intensity, ), row=2, col=1)
    fig.append_trace(go.Scatter(x=temperature, y=intensity), row=3, col=1)


    # Add the raw data
    # fig.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='markers', name='Data'))

    # Add the regression line
    #fig.add_trace(go.Scatter(x=[0, x_max], y=[evaluate_line(a, b, 0, 0),
    #                                          evaluate_line(a, b, 0, x_max)],
    #                         mode='lines', name='Regression line'))

    # Display the figure in a web browser
    fig.show()


# functions used to generate map with coordinates
def fire_intensity_and_location_by_month(year: int, month: str) -> List[Tuple[float, Tuple[float, float]]]:
    """Return a list of tuple of each fire in a month, with attributes of fire intensity
       and its latitude and longitude"""
    fires = [fire for fire in EXAMPLE_FIRE_DATASET[year][month]]

    accumulator = []
    for fire in fires:
        fire_size = fire[2]
        duration = (fire[1] - fire[0]).days + (fire[1] - fire[0]).seconds / (3600 * 24)
        location = fire[4]
        accumulator.append((fire_size * duration, location))

    return accumulator
