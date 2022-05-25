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