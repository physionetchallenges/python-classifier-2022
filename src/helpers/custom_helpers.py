#additional helper functions beyond those included in helper_code.py

def load_training_data(data_folder):
    #message: find data files
    if verbose >= 1:
        print('Finding data files...')

    # Find the patient data files.
    patient_files = find_patient_files(data_folder) #list of patient .txt files
    num_patient_files = len(patient_files)
    if num_patient_files==0:
        raise Exception('No data was provided.')

    #message: extract features and labels from data
    if verbose >= 1:
        print('Extracting features and labels from the Challenge data...')
    
    