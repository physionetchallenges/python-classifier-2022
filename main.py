#allows for easier method for locally running the model
#pass "train" or "run" as arguments when executing main.py

import os
import sys

action = sys.argv[1] #"train" or "run"; determines whether to train the model or run the model.

training_data_folder = "src/data/raw_training/training_data" #folder storing data for training the model
testing_data_folder = "src/data/raw_testing" #folder storing data for testing the model
model_folder = "src/model" #folder storing the model
output_folder = "src/out" #folder storing output of running the model

if action == "train":
	print("training model...")
	os.system("python src/train_model.py {} {}".format(training_data_folder, model_folder))
if action == "run":
	print("running model...")
	os.system("python src/run_model.py {} {} {}".format(model_folder, testing_data_folder, output_folder))
