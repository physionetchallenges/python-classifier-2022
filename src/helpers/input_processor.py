import os
import polars as pl

def ingestData(data_dir):

    id = []

    # nan, Adolescent, Infant, Child, Neonate
    age = []

    # Mail, Female
    sex = []

    # contains nan
    height = []

    # contains nan
    weight = []

    # True, False
    pregnant = []

    # Present, Absent, Unknown
    murmur = []

    audio_files = []

    print("Ingesting data from ", data_dir  )
    # Loop through all text files in the data directory
    
    for file in os.listdir(data_dir):
        if file.endswith(".txt"):
            # Open text file
            with open(data_dir + "/" + file, "r") as f:

                # Get first number, that is the id
                patientID = f.readline().split(" ")[0]
                id.append(patientID)       

                
                audio_array = []
                for line in f:

                    # find any words that end with .wav those are the audio files
                    moving_line = line.strip().split(" ")
                    for word in moving_line:
                        if word.endswith(".wav"):
                            audio_array.append(word)             

                    # Find line that starts with age
                    if line.startswith("#Age:"):
                        age.append(line.split(" ")[1].strip())

                    # Find line that starts with sex
                    if line.startswith("#Sex:"):
                        sex.append(line.split(" ")[1].strip())

                    # Find line that starts with height
                    if line.startswith("#Height:"):
                        height.append(line.split(" ")[1].strip())

                    # Find line that starts with weight
                    if line.startswith("#Weight:"):
                        weight.append(line.split(" ")[1].strip())
                    
                    # Find line that starts with pregnant
                    if line.startswith("#Pregnancy status:"):
                        pregnant.append(line.split(" ")[2].strip())

                    # Find line that starts with murmur
                    if line.startswith("#Murmur:"):
                        murmur.append(line.split(" ")[1].strip())
                audio_files.append(audio_array)

    #Create a polars object to store the data
    df = pl.DataFrame({
        "id": id,
        "age": age,
        "sex": sex,
        "height": height,
        "weight": weight,
        "pregnant": pregnant,
        "murmur": murmur,
        "audio_files": audio_files
    })
    
    return df

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

#PURPOSE:   produces the spectrogram of the specified .wav file
#PARAMS:    wav_file    str     path to the .wav file
#RETURNS:   ndarray of float32 - spectrogram of inputted .wav file
def wav_to_spectro(wav_file):
    sample_rate, samples = wavfile.read(wav_file)
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate)
    return spectrogram

#PURPOSE:   loads an invertable dictionary that allows for encoding/decoding patient features as numbers
#RETURNS:   tuple - a tuple containing the following elements:
#               dict - a dict object used to encode features. Each key stores the name of a feature as a string, and the corresponding value is a dict object (where each key is a possible feature_value stored as a str, and the corresponding value is a number used to encode for the feature_value)
#               dict - a dict object used to decode features. Each key stores the name of a feature as a string, and the corresponding value is a dict object (where each key is a number used to encode for a feature_value, and the corresponding value is the feature_value stored as a str)
def load_cipher():
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

    decode = {}
    for feature_name, feature_values in encode.items():
        decode[feature_name] = invert_dict(feature_values)

    return encode, decode


#PURPOSE:   inverts a dict object that obeys one-to-one mapping of ley-value pairs; the key and value of any given original key-value pair are the value and key of the new key-value pair, respectively.
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
        
#PURPOSE:   checks whether the value of a given feature is defined in a given string; if it is, appends this value to var
#PARAMS:    str_in      str     the string to check. function assumes this string is the form (str_in = some_feature + ": " + value), where (some_feature) is an arbitrary feature and (value) is the value of said feature.
#           feature     str     the feature to check for
#           var         list    the variable to append the value of the feature to, if applicable
def check_feature(str_in, feature, var):
    if not ": " in str_in:
        raise Exception('Expected str_in to contain ": ". Function assumes str_in is the form (str_in = some_feature + ": " + value), where (some_feature) is an arbitrary feature and (value) is the value of said feature.')
    if not type(var)==list:
        raise Exception('var is not of type list')

    if str_in.startswith(feature + ":"):
        var.append(str_in.split(": ", 1)[1].strip())