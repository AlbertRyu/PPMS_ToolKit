# PPMS Data Processing Kit

A tiny python package which helps you to extract and process the data from *Physical Property Measuring System* (PPMS)

## Usage

This light weight Python toolkit should helps you:

1. Transform the raw_data in a more easy-to-operate format (Numpy Array or Pandas Dataframe)
2. Plot the data for a quick review.
3. Do some data processing. (e.g. Phonon background subtraction.)
4. Fit the data and extract the fit parametees. (e.g. Currie Temperature)

## Data Structure

This kit essentially contains two object: Sample and Measurements

**Sample** contains info such as Name, Mass, Make_time, etc for a Sample. It also contains a list of Measurements assigned to this sample.

**Measurement** contains info of a certain measurement, and contains different kinds of information and internal function depending on its kind.

Sample and Measurement could be created and processed separetly, but they are recommended to be linked. Each Measurement should be assgined to a certain sample. But you could create and process a Measurement without asigning it to a sample. You could also create a sample with info but add measurements to it afterwards.

*Currently Supported Measurements:*

```text
Measurements 
├── HeatCapacityMeasurement 
└── MagnetismMeasurement 
    ├── MT 
    └── MH 
```

## Save and Load

After entering the experimental metadata (e.g. sample mass, name) and processing the .dat file, you can store the current state of the sample into a .pkl file using Python’s built-in pickle module. This allows for easy reloading without needing to reprocess the raw data.
