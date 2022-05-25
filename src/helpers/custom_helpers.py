#additional helper functions beyond those included in helper_code.py
from helper_code import *
import polars as pl
import pandas as pd
from scipy import signal
from scipy.io import wavfile
from input_processor import *

def load_training_data(data_folder):
    data_labels = [] #TODO: implement this
    #encode: a python dictionary that allows for encoding features as numbers.
    encode = {
        'Age':                      {'Neonate': 0.5, 'Infant': 6, 'Child': 6*12, 'Adolescent': 15*12, 'Young Adult': 20*12}, #represent each age group as the approximate number of months for the middle of the age group
        'Sex':                      {'Male': 0, 'Female': 1},
        'Pregnancy status':         {'True': 1, 'False': 0},
        'Murmur':                   {'Present': 1, 'Absent': 0, 'Unkown': 2},
        'location':                 {'PV': 0, 'TV': 1, 'AV': 2, 'MV': 3, 'Phc': 4},
        'Systolic murmur timing':   {'Early-systolic': 0, 'Holosystolic': 1, 'Mid-systolic': 2, 'Late-systolic': 3},
        'Systolic murmur shape':    {'Crescendo': 0, 'Decrescendo': 1, 'Diamond': 2, 'Plateau': 3},
        'Systolic murmur pitch':    {'Low': 0, 'Medium': 1, 'High': 2},
        'Systolic murmur grading':  {'I/VI': 0, 'II/VI': 1, 'III/VI': 2},
        'Systolic murmur quality':  {'Blowing': 0, 'Harsh': 1, 'Musical': 2},
        'Diastolic murmur timing':  {'Early-diastolic': 0, 'Holodiastolic': 1, 'Mid-diastolic': 2},
        'Diastolic murmur shape':   {'Crescendo': 0, 'Decrescendo': 1, 'Diamond': 2, 'Plateau': 3}, #note: only decresendo and plateau are actually used, other items are included for consistency with 'systolic murmur shape'
        'Diastolic murmur pitch':   {'Low': 0, 'Medium': 1, 'High': 2},
        'Diastolic murmur grading': {'I/IV': 0, 'II/IV': 1, 'III/IV': 2},
        'Diastolic murmur quality': {'Blowing': 0, 'Harsh': 1, 'Musical': 2}, #note: only blowing and harsh are actually used, other items are included for consistency with 'systolic murmur quality'
        'Outcome':                  {'Abnormal': 0, 'Normal': 1}
    }

    #Produce list of all patient .txt files, eg. ["folder1/folder2/patientfile1.txt", "folder1/folder2/patientfile2.txt", "..."]
    patient_files = find_patient_files(data_folder)
    num_patient_files = len(patient_files)
    if num_patient_files==0:
        raise Exception('No data was provided.')

    #initialize master dataframe to store all data
    df_master = pd.DataFrame(columns = data_labels)

    #iterate through each patient, get patient's data, and add it to master dataframe
    for current_patient in patient_files:
        #initialize dataframe to store current patient's data
        df = pd.DataFrame(columns = data_labels)

        #load current patient's data as a string
        current_patient_data = load_patient_data(patient_files[current_patient])

        #get list of all recordings for current patient, add each as a row to df
        recordings = list_patient_recordings(current_patient_data)

        #get features from patient data, fill in rows of df appropriately

        #append df to master_df
    