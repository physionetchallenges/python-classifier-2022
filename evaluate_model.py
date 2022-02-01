#!/usr/bin/env python

# Do *not* edit this script. Changes will be discarded so that we can process the models consistently.

# This file contains functions for evaluating models for the 2022 Challenge. You can run it as follows:
#
#   python evaluate_model.py labels outputs scores.csv class_scores.csv
#
# where 'labels' is a folder containing files with the labels, 'outputs' is a folder containing files with the outputs from your
# model, 'scores.csv' (optional) is a collection of scores for the algorithm outputs, # and 'class_scores.csv' (optional) is a
# collection of per-class scores for the algorithm outputs.
#
# Each label or output file must have the format described on the Challenge webpage. The scores for the algorithm outputs include
# the area under the receiver-operating characteristic curve (AUROC), the area under the recall-precision curve (AUPRC), accuracy,
# macro F-measure, and the Challenge score.

import os, os.path, sys, numpy as np
from helper_code import load_patient_data, get_label, load_challenge_outputs, compare_strings

# Evaluate the model.
def evaluate_model(label_folder, output_folder):
    # Define classes.
    classes = ['Present', 'Unknown', 'Absent']

    # Load the label and output files and reorder them, if needed, for consistency.
    label_files, output_files = find_challenge_files(label_folder, output_folder)
    labels = load_labels(label_files, classes)
    binary_outputs, scalar_outputs = load_classifier_outputs(output_files, classes)

    # For each patient, set the 'Unknown' class to positive if no class is positive or if multiple classes are positive.
    labels = enforce_positives(labels, classes, 'Unknown')
    binary_outputs = enforce_positives(binary_outputs, classes, 'Unknown')

    # Evaluate the model by comparing the labels and outputs.
    auroc, auprc, auroc_classes, auprc_classes = compute_auc(labels, scalar_outputs)
    accuracy = compute_accuracy(labels, binary_outputs)
    f_measure, f_measure_classes = compute_f_measure(labels, binary_outputs)
    challenge_score = compute_challenge_score(labels, binary_outputs, classes)

    # Return the results.
    return classes, auroc, auprc, auroc_classes, auprc_classes, accuracy, f_measure, f_measure_classes, challenge_score

# Find Challenge files.
def find_challenge_files(label_folder, output_folder):
    label_files = list()
    output_files = list()
    for label_file in sorted(os.listdir(label_folder)):
        label_file_path = os.path.join(label_folder, label_file) # Full path for label file
        if os.path.isfile(label_file_path) and label_file.lower().endswith('.txt') and not label_file.lower().startswith('.'):
            root, ext = os.path.splitext(label_file)
            output_file = root + '.csv'
            output_file_path = os.path.join(output_folder, output_file) # Full path for corresponding output file
            if os.path.isfile(output_file_path):
                label_files.append(label_file_path)
                output_files.append(output_file_path)
            else:
                raise IOError('Output file {} not found for label file {}.'.format(output_file, label_file))

    if label_files and output_files:
        return label_files, output_files
    else:
        raise IOError('No label or output files found.')

# Load labels from header/label files.
def load_labels(label_files, classes):
    num_patients = len(label_files)
    num_classes = len(classes)

    # Use one-hot encoding for the labels.
    labels = np.zeros((num_patients, num_classes), dtype=np.bool_)

    # Iterate over the patients.
    for i in range(num_patients):
        data = load_patient_data(label_files[i])
        label = get_label(data)
        for j, x in enumerate(classes):
            if compare_strings(label, x):
                labels[i, j] = 1

    return labels

# Load outputs from output files.
def load_classifier_outputs(output_files, classes):
    # The outputs should have the following form:
    #
    # #Record ID
    # class_1, class_2, class_3
    #       0,       1,       1
    #    0.12,    0.34,    0.56
    #
    num_patients = len(output_files)
    num_classes = len(classes)

    # Use one-hot encoding for the outputs.
    binary_outputs = np.zeros((num_patients, num_classes), dtype=np.bool_)
    scalar_outputs = np.zeros((num_patients, num_classes), dtype=np.float64)

    # Iterate over the patients.
    for i in range(num_patients):
        patient_id, patient_classes, patient_binary_outputs, patient_scalar_outputs = load_challenge_outputs(output_files[i])

        # Allow for unordered or reordered classes.
        for j, x in enumerate(classes):
            for k, y in enumerate(patient_classes):
                if compare_strings(x, y):
                    binary_outputs[i, j] = patient_binary_outputs[k]
                    scalar_outputs[i, j] = patient_scalar_outputs[k]

    return binary_outputs, scalar_outputs

# For each patient, set a specific class to positive if no class is positive or multiple classes are positive.
def enforce_positives(outputs, classes, positive_class):
    num_patients, num_classes = np.shape(outputs)
    j = classes.index(positive_class)

    for i in range(num_patients):
        if np.sum(outputs[i, :])!=1:
            outputs[i, :] = 0
            outputs[i, j] = 1
    return outputs

# Compute a binary confusion matrix, where the columns are expert labels and rows are classifier labels.
def compute_confusion_matrix(labels, outputs):
    assert(np.shape(labels)==np.shape(outputs))
    assert(all(value in (0, 1) for value in np.unique(labels)))
    assert(all(value in (0, 1) for value in np.unique(outputs)))

    num_patients, num_classes = np.shape(labels)

    A = np.zeros((num_classes, num_classes))
    for k in range(num_patients):
        i = np.argmax(outputs[k, :])
        j = np.argmax(labels[k, :])
        A[i, j] += 1

    return A

# Compute binary one-vs-rest confusion matrices, where the columns are expert labels and rows are classifier labels.
def compute_one_vs_rest_confusion_matrix(labels, outputs):
    assert(np.shape(labels)==np.shape(outputs))
    assert(all(value in (0, 1) for value in np.unique(labels)))
    assert(all(value in (0, 1) for value in np.unique(outputs)))

    num_patients, num_classes = np.shape(labels)

    A = np.zeros((num_classes, 2, 2))
    for i in range(num_patients):
        for j in range(num_classes):
            if labels[i, j]==1 and outputs[i, j]==1: # TP
                A[j, 0, 0] += 1
            elif labels[i, j]==0 and outputs[i, j]==1: # FP
                A[j, 0, 1] += 1
            elif labels[i, j]==1 and outputs[i, j]==0: # FN
                A[j, 1, 0] += 1
            elif labels[i, j]==0 and outputs[i, j]==0: # TN
                A[j, 1, 1] += 1

    return A

# Compute macro AUROC and macro AUPRC.
def compute_auc(labels, outputs):
    num_patients, num_classes = np.shape(labels)

    # Compute and summarize the confusion matrices for each class across at distinct output values.
    auroc = np.zeros(num_classes)
    auprc = np.zeros(num_classes)

    for k in range(num_classes):
        # We only need to compute TPs, FPs, FNs, and TNs at distinct output values.
        thresholds = np.unique(outputs[:, k])
        thresholds = np.append(thresholds, thresholds[-1]+1)
        thresholds = thresholds[::-1]
        num_thresholds = len(thresholds)

        # Initialize the TPs, FPs, FNs, and TNs.
        tp = np.zeros(num_thresholds)
        fp = np.zeros(num_thresholds)
        fn = np.zeros(num_thresholds)
        tn = np.zeros(num_thresholds)
        fn[0] = np.sum(labels[:, k]==1)
        tn[0] = np.sum(labels[:, k]==0)

        # Find the indices that result in sorted output values.
        idx = np.argsort(outputs[:, k])[::-1]

        # Compute the TPs, FPs, FNs, and TNs for class k across thresholds.
        i = 0
        for j in range(1, num_thresholds):
            # Initialize TPs, FPs, FNs, and TNs using values at previous threshold.
            tp[j] = tp[j-1]
            fp[j] = fp[j-1]
            fn[j] = fn[j-1]
            tn[j] = tn[j-1]

            # Update the TPs, FPs, FNs, and TNs at i-th output value.
            while i < num_patients and outputs[idx[i], k] >= thresholds[j]:
                if labels[idx[i], k]:
                    tp[j] += 1
                    fn[j] -= 1
                else:
                    fp[j] += 1
                    tn[j] -= 1
                i += 1

        # Summarize the TPs, FPs, FNs, and TNs for class k.
        tpr = np.zeros(num_thresholds)
        tnr = np.zeros(num_thresholds)
        ppv = np.zeros(num_thresholds)
        for j in range(num_thresholds):
            if tp[j] + fn[j]:
                tpr[j] = float(tp[j]) / float(tp[j] + fn[j])
            else:
                tpr[j] = float('nan')
            if fp[j] + tn[j]:
                tnr[j] = float(tn[j]) / float(fp[j] + tn[j])
            else:
                tnr[j] = float('nan')
            if tp[j] + fp[j]:
                ppv[j] = float(tp[j]) / float(tp[j] + fp[j])
            else:
                ppv[j] = float('nan')

        # Compute AUROC as the area under a piecewise linear function with TPR/
        # sensitivity (x-axis) and TNR/specificity (y-axis) and AUPRC as the area
        # under a piecewise constant with TPR/recall (x-axis) and PPV/precision
        # (y-axis) for class k.
        for j in range(num_thresholds-1):
            auroc[k] += 0.5 * (tpr[j+1] - tpr[j]) * (tnr[j+1] + tnr[j])
            auprc[k] += (tpr[j+1] - tpr[j]) * ppv[j+1]

    # Compute macro AUROC and macro AUPRC across classes.
    if np.any(np.isfinite(auroc)):
        macro_auroc = np.nanmean(auroc)
    else:
        macro_auroc = float('nan')
    if np.any(np.isfinite(auprc)):
        macro_auprc = np.nanmean(auprc)
    else:
        macro_auprc = float('nan')

    return macro_auroc, macro_auprc, auroc, auprc

# Compute accuracy.
def compute_accuracy(labels, outputs):
    A = compute_confusion_matrix(labels, outputs)

    if np.sum(A) > 0:
        accuracy = np.sum(np.diag(A)) / np.sum(A)
    else:
        accuracy = float('nan')

    return accuracy

# Compute macro F-measure.
def compute_f_measure(labels, outputs):
    num_patients, num_classes = np.shape(labels)

    A = compute_one_vs_rest_confusion_matrix(labels, outputs)

    f_measure = np.zeros(num_classes)
    for k in range(num_classes):
        tp, fp, fn, tn = A[k, 0, 0], A[k, 0, 1], A[k, 1, 0], A[k, 1, 1]
        if 2 * tp + fp + fn > 0:
            f_measure[k] = float(2 * tp) / float(2 * tp + fp + fn)
        else:
            f_measure[k] = float('nan')

    if np.any(np.isfinite(f_measure)):
        macro_f_measure = np.nanmean(f_measure)
    else:
        macro_f_measure = float('nan')

    return macro_f_measure, f_measure

# Compute Challenge score.
def compute_challenge_score(labels, outputs, classes):
    # Define costs. Load these costs from an external file instead of defining them here.
    c_algorithm =     1
    c_expert    =   250
    c_treatment =  1000
    c_error     = 10000
    alpha       =   0.5

    num_patients, num_classes = np.shape(labels)

    A = compute_confusion_matrix(labels, outputs)

    idx_positive = classes.index('Present')
    idx_unknown = classes.index('Unknown')
    idx_negative = classes.index('Absent')

    n_tp  = A[idx_positive, idx_positive]
    n_fpu = A[idx_positive, idx_unknown ]
    n_fp  = A[idx_positive, idx_negative]
    n_fup = A[idx_unknown , idx_positive]
    n_tu  = A[idx_unknown , idx_unknown ]
    n_fun = A[idx_unknown , idx_negative]
    n_fn  = A[idx_negative, idx_positive]
    n_fnu = A[idx_negative, idx_unknown ]
    n_tn  = A[idx_negative, idx_negative]

    n_positive = n_tp  + n_fup + n_fn
    n_unknown  = n_fpu + n_tu  + n_fnu
    n_negative = n_fp  + n_fun + n_tn

    n_total = n_positive + n_unknown + n_negative

    total_score = c_algorithm * n_total \
        + c_expert * (n_tp + 2 * n_fpu + n_fp + n_fup + 2 * n_tu + n_fun) \
        + c_treatment * (n_tp + alpha * n_fpu + n_fup + alpha * n_tu) \
        + c_error * (n_fn + alpha * n_fnu)
    challenge_score = total_score / n_total

    return challenge_score

if __name__ == '__main__':
    classes, auroc, auprc, auroc_classes, auprc_classes, accuracy, f_measure, f_measure_classes, challenge_score = evaluate_model(sys.argv[1], sys.argv[2])
    output_string = 'AUROC,AUPRC,Accuracy,F-measure,Challenge\n{:.3f},{:.3f},{:.3f},{:.3f},{:.3f}'.format(auroc, auprc, accuracy, f_measure, challenge_score)
    class_output_string = 'Classes,{}\nAUROC,{}\nAUPRC,{}\nF-measure,{}'.format(
        ','.join(classes),
        ','.join('{:.3f}'.format(x) for x in auroc_classes),
        ','.join('{:.3f}'.format(x) for x in auprc_classes),
        ','.join('{:.3f}'.format(x) for x in f_measure_classes))

    if len(sys.argv) == 3:
        print(output_string)
    elif len(sys.argv) == 4:
        with open(sys.argv[3], 'w') as f:
            f.write(output_string)
    elif len(sys.argv) == 5:
        with open(sys.argv[3], 'w') as f:
            f.write(output_string)
        with open(sys.argv[4], 'w') as f:
            f.write(class_output_string)
