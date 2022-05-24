#additional helper functions beyond those included in helper_code.py
from helper_code import *
import polars as pl
import pandas as pd
from scipy import signal
from scipy.io import wavfile

def load_training_data(data_folder):
    data_labels = ['a','b','c'] #TODO: implement data labels

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
    

#PURPOSE:   Returns the file name of all recordings (.wav file) listed in a given patient file. Does not specify path to file locations.
#PARAMS:    patient_data    str     patient data as a string, obtained using load_patient_data(find_patient_files(data_folder)) from helper_code.py
#RETURNS:   list of str - each element stores the filename of one recording, list contains filenames of all recordings described by patient file
def list_patient_recordings(patient_data):
    recordings = list()
    num_locations = get_num_locations(patient_data)

    all_referenced_files = patient_data.split('\n')[1:num_locations+1]
    for i in range(len(all_referenced_files)):
        current_row = all_referenced_files[i].split(' ')
        recordings.append(current_row[2])

    if not recordings:
        raise Exception("No recordings were found in the following patient data: \n*BEGIN PATIENT DATA* \n{} \n*END PATIENT DATA*".format(patient_data))

    return recordings

#PURPOSE:   produces the spectogram of the specified .wav file
#PARAMS:    wav_file    str     path to the .wav file
#RETURNS:   ndarray of float32 - spectrogram of inputted .wav file
def wav_to_spectrogram(wav_file):
    sample_rate, samples = wavfile.read('data/raw_training/training_data/2530_AV.wav')
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
    return spectrogram