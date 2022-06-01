###########################################################################################################
# THIS CONTAINS LOOK UP TABLES FOR OTHER FUNCTIONS TO MINIMIZE THERE SIZE AND TO MAKE SHARING CODE EASIER #
###########################################################################################################

clinical_data = {
        'patient_id':           [],
        'num_locations':        [],
        'sampling_frequency':   [],
        'audio_files':          [],
        'recording_locations':  [],
        #begin named features
        'age':                  [],
        'sex':                  [],
        'height':               [],
        'weight':               [],
        'pregnancy_status':     [],
        'murmur':               [],
        'murmur_locations':     [],
        'most_audible_location':[],
        'sys_mur_timing':       [],
        'sys_mur_shape':        [],
        'sys_mur_pitch':        [],
        'sys_mur_grading':      [],
        'sys_mur_quality':      [],
        'dia_mur_timing':       [],
        'dia_mur_shape':        [],
        'dia_mur_pitch':        [],
        'dia_mur_grading':      [],
        'dia_mur_quality':      [],
        'outcome':              [],
        'campaign':             [],
        'additional_id':        []
    }


clinical_iterables = {
    'age':                  '#Age',
    'sex':                  '#Sex',
    'height':               '#Height',
    'weight':               '#Weight',
    'pregnancy_status':     '#Pregnancy status',
    'murmur':               '#Murmur',
    'murmur_locations':     '#Murmur locations',
    'most_audible_location':'#Most audible location',
    'sys_mur_timing':       '#Systolic murmur timing',
    'sys_mur_shape':        '#Systolic murmur shape',
    'sys_mur_pitch':        '#Systolic murmur pitch',
    'sys_mur_grading':      '#Systolic murmur grading',
    'sys_mur_quality':      '#Systolic murmur quality',
    'dia_mur_timing':       '#Diastolic murmur timing',
    'dia_mur_shape':        '#Diastolic murmur shape',
    'dia_mur_pitch':        '#Diastolic murmur pitch',
    'dia_mur_grading':      '#Diastolic murmur grading',
    'dia_mur_quality':      '#Diastolic murmur quality',
    'outcome':              '#Outcome',
    'campaign':             '#Campaign',
    'additional_id':        '#Additional ID'
}