#helper functions that are now deprecated or no longer in use
#If using one of these functions, first move it to an appropriate helper file

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

#PURPOSE:   checks whether the value of a given feature is defined in a given string; if it is, appends this value to var
#PARAMS:    str_in      str     the string to check. function assumes this string has the form (str_in = some_feature + ": " + value), where (some_feature) is an arbitrary feature and (value) is the value of said feature.
#           check_for   str     the feature to check for
#           var         list    the variable to append the value of the feature to, if applicable
def check_feature(str_in, check_for, var):
    if not ": " in str_in:
        raise Exception('Expected str_in to contain ": ". Function assumes str_in has the form (str_in = some_feature + ": " + value), where (some_feature) is an arbitrary feature and (value) is the value of said feature.')
    if not type(var)==list:
        raise Exception('var is not of type list')

    if str_in.startswith(check_for + ":"):
        var.append(str_in.split(": ", 1)[1].strip())