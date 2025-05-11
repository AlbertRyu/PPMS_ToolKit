# PPMS Data Processing Kit

*Physical Property Measuring System*, short for PPMS, is a powerful instrument which allows us to acquire, as its name, many different physics properties of different kinds of sample to a good precision.

## Usage

This small toolkit written in Python should help you to:

1. Transfrom the raw_data in a more easy-to-operate format (Numpy Array or Pandas Dataframe)
2. Plot the data for a quick review.
3. Do some data processing. (e.g. Phonon background subtraction.)
4. Fit the data and extract the fit parametees. (e.g. Currie Temperature)

## Data Structur

'''
-- Sample
-- Measurements -- HeatCapacityMeasurement
                -- MagnetismMeasurment      -- MT
                                            -- MH
'''

'''js
This is a code block
'''


## Save and Load

After you input the experiement information (such as Sample Mass, Sample Name) and the 