"""
RUSH Auto Works Constants
=========================

Constant values that are used throughout the analysis.
"""

from .units import u

#### DEFINE CONSTANTS FOR CALCS ####
MASS_DRIVER = 80 * u.kg
"""Assumed mass of the driver"""
MASS_CAR = 513 * u.kg                       # https://rushautoworks.com/car_post/rush-sr/#:~:text=Weight%3A%20513kg%20/%201130lbs
"""Mass of just the vehicle"""

VEHICLE_WIDTH = 1500 * u.mm                 # https://rushautoworks.com/car_post/rush-sr/#:~:text=Wheelbase%3A%201900mm%20/%2075%E2%80%B3-,Width%3A%201500mm%20/%2059%E2%80%B3,-Height%3A%20990mm%20/%2038.9
"""Width of the vehicle"""
VEHICLE_HEIGHT = 990 * u.mm                 # https://rushautoworks.com/car_post/rush-sr/#:~:text=Height%3A%20990mm%20/%2038.9%E2%80%B3
"""Height of the vehicle"""
VEHICLE_LENGTH = 3325 * u.mm                # https://rushautoworks.com/wp-content/uploads/2023/03/2023-Rush-SR-Brochure.pdf
"""Length of the vehicle"""

POWER_GAS_AT_WHEELS = 145 * u.hp            # https://rushautoworks.com/wp-content/uploads/2023/03/2023-Rush-SR-Brochure.pdf
"""Power provided by the gas engine at the wheels"""
PEAK_GAS_RPM = 11800 * u.rpm                # https://rushautoworks.com/wp-content/uploads/2023/03/2023-Rush-SR-Brochure.pdf
"""Peak rpm of the gas engine"""

RADIUS_WHEEL_FRONT = 276 * u.mm             # https://www.nankangtyre.co.uk/products/motorsport/ar-1/
"""Radius of the front tires"""
RADIUS_WHEEL_BACK = 288 * u.mm              # https://www.nankangtyre.co.uk/products/motorsport/ar-1/
"""Radius of the rear tires"""

RHO_AIR = 1.2041 * (u.kg / (u.m**3))        # Air density at 20 degrees C
"""Density of air at 20 degrees C"""
####################################


#### DERIVED CONSTANTS ####
VEHICLE_CROSS_SECTIONAL_AREA = VEHICLE_HEIGHT * VEHICLE_WIDTH
"""Frontal cross sectional area of the vehicle"""

MASS_VEHICLE = MASS_DRIVER + MASS_CAR
"""Mass of the vehicle including the driver"""
###########################


#### DIRECTORIES ####
DATA_DIRECTORY = 'data/formatted'
"""Directory containing all of the parseable data"""
PLOTS_DIRECTORY = 'plots'
"""Directory containing all of the plots"""
LAP_TIMES_FILEPATH = 'data/lap_times.json'
"""File containing lap time data for each data-file in the data directory"""
#####################
