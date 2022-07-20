"""
Contains all functions needed to calculate the growth of
seaweed.

The calculation for each factor is split into two functions.
The first function with "single_value" in the name calculates
the factor for a single value. While the second function with
"calculate" in the name calculates the factor for a whole dataframe,
for which it uses the first function.

Based on the publication:
James, S.C. and Boriah, V. (2010), Modeling algae growth
in an open-channel raceway
Journal of Computational Biology, 17(7), 895−906.
"""
import math
import pandas as pd

def growth_factor_combination_single_value(illumination_factor:float,
                                            temperature_factor:float,
                                            nutrient_factor:float,
                                            salinity_factor:float):
    """
    Calculates the actual production rate of the seaweed
    Arguments:
        illumination_factor: the illumination factor
        temperature_factor: the temperature factor
        nutrient_factor: the nutrient factor
        salinity_factor: the salinity factor
    Returns:
        The actual production rate of the algae
    """
    # Make sure all factors are between 0 and 1
    factors = [illumination_factor, temperature_factor, 
            nutrient_factor, salinity_factor]
    for factor in factors:
        assert 0 <= factor <= 1
    # Calculate the actual production rate
    return illumination_factor * temperature_factor * \
           nutrient_factor * salinity_factor

def growth_factor_combination(
                                non_opt_illumniation:pd.DataFrame,
                                non_opt_temperature:pd.DataFrame,
                                non_opt_nutrients:pd.DataFrame,
                                non_opt_salinity:pd.DataFrame):
    """
    Calculates the actual production rate of the seaweed for a whole dataframe
    And returns it as a pandas dataframe
    """
    factors_combined_df = pd.concat([non_opt_illumniation,
                                    non_opt_temperature,
                                    non_opt_nutrients,
                                    non_opt_salinity],
                                    axis=1)
    factors_combined_df.columns = [
                                    'non_opt_illumniation',
                                    'non_opt_temperature',
                                    'non_opt_nutrients',
                                    'non_opt_salinity'] # Rename the columns

    factors_combined_df["growth_factor_combination"] = factors_combined_df.apply(
        lambda x: growth_factor_combination_single_value(
                                                        x['non_opt_illumniation'],
                                                        x['non_opt_temperature'],
                                                        x['non_opt_nutrients'],
                                                        x['non_opt_salinity']),
                                                        axis=1) # Calculate the growth factor combination
    return factors_combined_df['growth_factor_combination']


def illumination_single_value(illumination:float):
    """
    Calculates the illumination factor for a single value
    Arguments:
        illumination: the illumination of the algae in W/m²
    Returns:
        The illumination factor
    """
    if illumination < 21.9:
        return illumination / 21.9
    elif illumination > 100:
        return 100 / illumination
    else:
        return 1


def calculate_illumination_factor(illumination:pd.DataFrame):
    """
    Calculates the illumination factor for a whole dataframe
    """
    return illumination.apply(illumination_single_value)


def temperature_single_value(temperature:float):
    """
    Calculates the temperature factor
    Arguments:
        temperature: the temperature of the water in °C
    Returns:
        The temperature factor as a float
    """
    # where Kt1 = 0.017°C−2 and Kt2 = 0.06°C−2. These coefficients were determined by 
    # fitting the preceding equation such that g(15°C) = 0.25 and g(36°C) = 0.1
    
    
    kt1 = 0.017
    kt2 = 0.06

    if temperature < 24:
        return math.exp(-kt1 * (24 - temperature)**2)
    elif temperature > 30:
        return math.exp(-kt2 * (temperature - 30)**2)
    else:
        return 1


def calculate_temperature_factor(temperature:pd.DataFrame):
    """
    Calculates the temperature factor for a whole dataframe column
    Arguments:
        temperature: the temperature of the water in celcius
    Returns:
        The temperature factor as a pandas dataframe
    """
    # Apply the function to the salinity dataframe
    return temperature.apply(salinity_single_value)


def nutrient_single_value(nitrate:float, ammonium:float, phosphate:float):
    """
    Calculates the nutrient factor, which is the minimum of the 
    three nutrients nitrate, ammonium and phosphate for a single value
    Arguments:
        nitrate: the nitrate concentration in mg/L
        ammonium: the ammonium concentration in mg/L
        phosphate: the phosphate concentration in mg/L
    Returns:
        The nutrient factor as a float
    """
    # where KNO3 = 0.4 μM, KNH4 = 0.3 μM, and KPO4 = 0.1 μM.
    # were implemented because these yield growth rates consistent with  observations by Lapointe [1987]
    # "Phosphorus- and nitrogen-limited photosynthesis and growth of Gracilaria tikvahiae (Rhodophyceae)
    # in the Florida Keys: an experimental field study"
    kno3 = 0.4
    knh4 = 0.3
    kpo4 = 0.1
    # Calculate the single nutrient factors
    nitrate_factor = nitrate / (kno3 + nitrate)
    ammonium_factor = ammonium / (knh4 + ammonium)
    phosphate_factor = phosphate / (kpo4 + phosphate)
    # Calculate the nutrient factor
    return min(nitrate_factor, ammonium_factor, phosphate_factor)


def calculate_nutrient_factor(nitrate:pd.DataFrame,
                              ammonium:pd.DataFrame,
                              phosphate:pd.DataFrame):
    """
    Calculates the nutrient factor for a whole dataframe
    And returns the nutrient factor as a pandas dataframe
    """
    nutrient_df = pd.concat([nitrate, ammonium, phosphate], axis=1)
    nutrient_df.columns = ['nitrate', 'ammonium', 'phosphate']
    nutrient_df["nutrient_factor"] = nutrient_df.apply(
        lambda x: nutrient_single_value(x['nitrate'], x["ammonium"], x["phosphate"]), axis=1)

    return nutrient_df["nutrient_factor"]


def salinity_single_value(salinity:float):
    """
    Calculates the salinity factor for a single salinity value
    """
    # with  = 0.007 ppt−2 and = 0.063 ppt−2.
    kS1 = 0.007
    kS2 = 0.063
    if salinity < 24:
        return math.exp(-kS1 * (24 - salinity)**2)
    elif salinity > 36:
        return math.exp(-kS2 * (salinity - 36)**2)
    else:
        return 1


def calculate_salinity_factor(salinity:pd.DataFrame):
    """
    Calculates the salinity factor for a whole dataframe
    Arguments:
        salinity: the salinity of the water in ppt
    Returns:
        The salinity factor as a pandas dataframe
    """
    # Apply the function to the salinity dataframe
    return salinity.apply(salinity_single_value)
