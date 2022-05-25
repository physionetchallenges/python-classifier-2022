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