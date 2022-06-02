import os
from pydoc import cli
import polars as pl
import numpy as np
import helpers.audio_tools as adt
from lut import clinical_iterables, clinical_data
import copy 


def ingestData(data_dir):
    print("Ingesting data from ", data_dir  )
    # we use the deepcopy function to avoid overwriting the original clinical_iterables
    # otherwise this creates a super hard to find bug where running the code multiple times
    # will result in the output being different each time
    data = copy.deepcopy(clinical_data)
    for file in os.listdir(data_dir):
        if file.endswith(".txt"):
            # open text file
            with open(data_dir + "/" + file, "r") as f:
                # read first line
                line = f.readline()
                # split line into list
                line = line.strip().split(" ")
                data['patient_id'].append(line[0])
                data['num_locations'].append(line[1])
                data['sampling_frequency'].append(line[2])
                
                # loop through each line to check if it maches with an iterables
                audio_files = []
                recording_locations = []
                for line in f:
                    # check if line contains .wav
                    if ".wav" in line:
                        # split the line 
                        line_split = line.split(" ")
                        audio_files.append(line_split[2]) 
                        recording_locations.append(line_split[0]) 


                    for iterable in clinical_iterables:
                        if line.startswith(clinical_iterables[iterable] + ":"):
                            # get the value of the iterable
                            value = line.split(': ', 1)[1].strip()
                            # add the value to the data
                            data[iterable].append(value)
                data['audio_files'].append(audio_files)
                data['recording_locations'].append(recording_locations)
    df = pl.DataFrame(data)
    return df


#TODO: when exploding audio,files, only some locations have murmurs, address this

#PURPOSE:   load training data for input into ML model
#PARAMS:    data_dir    str         path to directory containing training data files
#           features    list(str)   list of features to pass to ML model
#RETURNS:   pl.DataFrame    dataframe storing spectrograms and features
def load_training_data(features, data_dir, nan, encode=False):

    #load data into dataframe
    df = ingestData(data_dir, nan, encode=encode)

    #interpret features=['*']
    if features==['*']:
        features = df.columns

    #get the spectrograms for each wav file, add as column to df
    df = df.explode('audio_files').with_column(
        pl.struct([pl.col('audio_files').str.replace(r"^", data_dir + '/').alias('file_paths'), 'sampling_frequency']) #specifiy the path to the wav files
        .apply(lambda x: adt.wav_to_spectro(x['file_paths'], x['sampling_frequency'])).alias('spectrogram') #call wav_to_spectro for each wav file
    )

    #get the spectrograms with the desired features
    out = df.select(pl.col(['spectrogram', *features]))

    return out

#PURPOSE:   loads an invertable dictionary that allows for encoding/decoding patient features as numbers
#PARAMS:    nan     any     value to encode 'nan' entries as
#RETURNS:   tuple - a tuple containing the following elements:
#               dict - a dict object used to encode features. Each key stores the name of a feature as a string, and the corresponding value is a dict object (where each key is a possible feature_value stored as a str, and the corresponding value is a number used to encode for the feature_value)
#               dict - a dict object used to decode features. Each key stores the name of a feature as a string, and the corresponding value is a dict object (where each key is a number used to encode for a feature_value, and the corresponding value is the feature_value stored as a str)
def load_cipher(nan):
    encode = {
        'recording_locations':  {'nan': nan, 'PV': 0, 'TV': 1, 'AV': 2, 'MV': 3, 'Phc': 4},
        'age':                  {'nan': nan, 'Neonate': 2, 'Infant': 26, 'Child': 6*52, 'Adolescent': 15*52, 'Young Adult': 20*52}, #represent each age group as the approximate number of weeks for the middle of the age group
        'sex':                  {'nan': nan, 'Male': 0, 'Female': 1},
        'pregnancy_status':     {'nan': nan, 'True': 1, 'False': 0},
        'murmur':               {'nan': nan, 'Present': 1, 'Absent': 0, 'Unknown': 2},
        'murmur_locations':     {'nan': nan, 'PV': 0, 'TV': 1, 'AV': 2, 'MV': 3, 'Phc': 4},
        'most_audible_location':{'nan': nan, 'PV': 0, 'TV': 1, 'AV': 2, 'MV': 3, 'Phc': 4},
        'sys_mur_timing':       {'nan': nan, 'Early-systolic': 0, 'Holosystolic': 1, 'Mid-systolic': 2, 'Late-systolic': 3},
        'sys_mur_shape':        {'nan': nan, 'Crescendo': 0, 'Decrescendo': 1, 'Diamond': 2, 'Plateau': 3},
        'sys_mur_pitch':        {'nan': nan, 'Low': 0, 'Medium': 1, 'High': 2},
        'sys_mur_grading':      {'nan': nan, 'I/VI': 0, 'II/VI': 1, 'III/VI': 2},
        'sys_mur_quality':      {'nan': nan, 'Blowing': 0, 'Harsh': 1, 'Musical': 2},
        'dia_mur_timing':       {'nan': nan, 'Early-diastolic': 0, 'Holodiastolic': 1, 'Mid-diastolic': 2},
        'dia_mur_shape':        {'nan': nan, 'Crescendo': 0, 'Decrescendo': 1, 'Diamond': 2, 'Plateau': 3}, #note: only decresendo and plateau are actually used, other items are included for consistency with 'systolic murmur shape'
        'dia_mur_pitch':        {'nan': nan, 'Low': 0, 'Medium': 1, 'High': 2},
        'dia_mur_grading':      {'nan': nan, 'I/IV': 0, 'II/IV': 1, 'III/IV': 2},
        'dia_mur_quality':      {'nan': nan, 'Blowing': 0, 'Harsh': 1, 'Musical': 2}, #note: only blowing and harsh are actually used, other items are included for consistency with 'systolic murmur quality'
        'outcome':              {'nan': nan, 'Abnormal': 0, 'Normal': 1}
    }

    decode = {}
    for feature_name, feature_values in encode.items():
        decode[feature_name] = invert_dict(feature_values)

    return encode, decode


#PURPOSE:   inverts a dict object that obeys one-to-one mapping of key-value pairs; the key and value of any given original key-value pair are the value and key of the new key-value pair, respectively.
#PARAMS:    dict_in     dict    the original dict object that is to be inverted
#RETURNS:   dict - the inverted dict object
def invert_dict(dict_in):
    #check that dict_in obeys one to one mapping
    keys_in = dict_in.keys()
    values_in = dict_in.values()
    if not (len(keys_in)==len(set(keys_in)) and len(values_in)==len(set(values_in))):
        raise Exception('The inputted dict object does not obey one to one mapping of key-value pairs')

    dict_out = {}
    for key, value in dict_in.items():
        dict_out[value] = key
    
    return dict_out