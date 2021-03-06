#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finding The Best Hyperparameters for Anomalies Detection on images
Date: 01/02/2021
Author: Diego Bueno (ID: 23567850) / Isabelle Sypott (ID: 21963427 )
e-mail: d.bueno.da.silva.10@student.scu.edu.au / i.sypott.10@student.scu.edu.au


Setting Hyperparameters according to parameters and return the model.

All results are also saved at CSV file for analyse.


"""

## importing the libraries required
import numpy as np
import sys
import pathlib
import random
import tensorflow as tf # using Tensorflow 2.4
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split #used to split data into training and test segments
from keras.callbacks import EarlyStopping, ModelCheckpoint 
#from keras import backend as K
#K.set_image_dim_ordering('tf') # Setting tensorflow-style ordering (NHWC).

## Importing especific functions used in this program 
path = str(pathlib.Path(__file__).resolve().parent) + "/"
sys.path.append(path)
from functions import *

    

# Setting Hyperparameters
def findingTheBestHyperparameters(resultsFile,                            
    noOfEpochs, # define number of epochs to execute
    myBatchSze, # size of each batch in interaction to get an epoch
    myTestSize, # how much have to be split for testing
    noOfFiles,  # number of batch files to process
    myMinDelta, # minimum improvement rate for do not early stop
    myPatience, # how many epochs run with improvement lower than myMinDelta 
    MyRandomSt, # random state for shuffling the data
    myMetric,  # type of metric used 
    MyOptimizer,# Optimeser
    MyLoss,     # Type of Loss
    MyLearnRate,# 0 value will keep default. Eg. adam => 0.001 
    noLayersCNN, 
    noFiltersCNN,# it will increase by plus 32 for each hidden layer
    hiddenActCNN,
    outputActCNN,
    dropOutsCNN,
    noLayersFNN, 
    noNeuronsFNN, # output layer. It will multly for each hidden layer 
    hiddenActFNN,
    outputActFNN,
    dropOutsFNN 
    ):

    # initialising variables
    data        = [] # array with all list of images read from batch files
    X           = [] # array with images data including channels (RGB)
    y           = [] # array with labels (index of category of images)
    myModelFile = path + "anomaliesDetectionModel.h5" # file to save trained model
    myResults   = path + resultsFile
    
    # Loading the data. "images/" folder must be in the same location of the script
    #
    # Structure of meta dictionary
    #
    ## meta dictionary:
        # {   
        # num_cases_per_batch': 10000
        #                      0           1            2       3        4       5        6        7         8         9
        # label_names': [b'airplane', b'automobile', b'bird', b'cat', b'deer', b'dog', b'frog', b'horse', b'ship', b'truck']
        # b'num_vis':    3072 ( 1024 R + 1024 G + 1024 B )   
        # } 
    meta = read( path + 'images/batches.meta')
    
    #
    # Structure of data dictionary
    #
    ## data: data_batch_N dictionary
        # { 
        # b'labels': b'training batch 5 of 5' => title of dictionary
        # b'labels': [1, 8... n ] => array 1D of size 10,000 labels
        # b'data': array([[255, 252, 253,..] , [127, 126, 127, ...], [...]] ) => array of size 10,000 x 3,072 ( 1024 R + 1024 G + 1024 B )
        # b'filenames': [b'compact_car_s_001706.png', b'icebreaker_s_001689.png',...] => array of size 10,000 with files names
        # }        
    for n in range(1,noOfFiles + 1,1):
        data = np.append(data, read( path + 'images/data_batch_' + str(n)) )
    
    # Unifying all images pixels values in unique array X with 50,000 images
    for images in data: # data = { data_batch_1, data_batch_2, data_batch_3, data_batch_4, data_batch5   }
        if len(X) == 0:
            X = images[b'data'] 
        else: # Need to concatenate instead append to create a unique array with 50,000 images
            X = np.concatenate((X, images[b'data']), axis=0)
        y = np.append(y, images[b'labels'] ) # y [ 0,1,2,3 ... 50,000] with 50,000 labels
    
    print("Shape of inputted data")        
    print("\nX shape with all images data: ", X.shape)
    print("y shape with all images labels", y.shape)
    
    # Selecting 40,000 instances for training set and 10,000 for test set
    [x_train, x_test, y_train, y_test] = train_test_split(X, y, test_size = myTestSize, random_state= MyRandomSt )
    
    print("\nShape of split data")
    print("\nx_train initial shape:  ", x_train.shape)
    print("x_test initial shape:  ", x_test.shape)
    print("y_train initial shape:  ", len(y_train))
    print("y_test initial shape:  ", len(y_test))
    print("\n")
     
    # Pre-processing to work with values between 0.0 and 1
    x_trainNormalised = x_train / 255.0
    x_testNormalised = x_test / 255.0
    
    ## Changing the shape of inputted data
    nInstancesTrain  = x_trainNormalised.shape[0]
    nInstancesTest   = x_testNormalised.shape[0]
    nRowns           = 32 
    nColumns         = 32
    nChannels        = 3  # 3 channels denotes one red, green and blue (RGB image)
    
    #x_trainNormalised= x_trainNormalised.reshape(   40,000,          32,     32,       3     )
    x_trainNormalised = x_trainNormalised.reshape(nInstancesTrain, nRowns, nColumns, nChannels) 
    
    #x_testNormalised = x_testNormalised.reshape(  10,000,        32,      32,       3     )
    x_testNormalised = x_testNormalised.reshape(nInstancesTest, nRowns, nColumns, nChannels)
    
    # Changing the shape of OUTPUT layer, also changing the labels of train and test into categorical data
    # It creates hot vectors for the classes like: [0. 0. 0. 1. 0. 0. 0. 0. 0. 0.]
    y_trainCategorical = to_categorical(y_train)
    y_testCategorical = to_categorical(y_test)
    
    # Checking that train and test data categorical and normalised are the correct shape for NN
    print("\nShape of normalised data")
    print("\nx_train normalised shape: ", x_trainNormalised.shape)
    print("x_test normalised shape: ", x_testNormalised.shape)
    print("y_trainCategorical shape: ", y_trainCategorical.shape)
    print("y_testCategorical shape: ", y_testCategorical.shape)
    print("\n\n")
    
    
    ## Loading previously trained model
    # If the model has been trained before, load it
    try:
        model = tf.keras.models.load_model(myModelFile,
                custom_objects={'f1_m': f1_m,
                                'precision_m': precision_m, 
                                'recall_m': recall_m, 
                                'fbetaprecisionskewed': fbetaprecisionskewed, 
                                'fbetarecallskewed': fbetarecallskewed})
        print("Model file " + myModelFile + " sucessfully loaded!\n")
        
    except OSError:
        print("Previously saved model does not exist.\n" +
              "Creating first file " + myModelFile + "\n")
    except:
        print("Error trying to open the file " + myModelFile +
              "\nCurrent file will be replaced!\n")
     
        
    ## Deploying the best configuration for Deep Neural Networking
    #  found by findingTheBestHyperparameters.py
    
    """  DROPOUT HINTS:
    In practice, you can usually apply dropout only to the neurons in the top one to three layers (excluding the output layer).
    (Aurelien pag. 481)
    
    In the simplest case, each unit is retained with a fixed probability p 
    independent of other units, where p can be chosen using a validation 
    set or can simply be set at 0.5, which seems to be close to optimal for 
    a wide range of networks and tasks. For the input units, however, 
    the optimal probability of retention is usually closer to 1 than to 0.5.
    (Dropout: A Simple Way to Prevent Neural Networks from Overfitting, 2014.)         
    """

    # tuning the Deep Neural Network 
    myModel = getMyModel( (nRowns, nColumns, nChannels), 
                   myMetric,
                   MyOptimizer,
                   MyLoss,
                   MyLearnRate,
                   noLayersCNN, 
                   noFiltersCNN,
                   hiddenActCNN,
                   outputActCNN,
                   dropOutsCNN,
                   noLayersFNN,
                   noNeuronsFNN,
                   hiddenActFNN,
                   outputActFNN,
                   dropOutsFNN)
    
    # Stopping early according to myMinDelta to avoid overfitting. Trained model saved at myModelFile
    myCallbacks = [EarlyStopping(monitor=myMetric, min_delta=myMinDelta , patience=myPatience, mode='auto'),
                 ModelCheckpoint(filepath=myModelFile, monitor=myMetric, save_best_only=True, verbose=1)]
     
    ## Training the model according to the labels and chose hyperparameters
    myModel.fit(x_trainNormalised, y_trainCategorical, epochs=noOfEpochs, batch_size=myBatchSze,  verbose=1, callbacks = myCallbacks)
    
    ## evaluating the accuracy using test data
    loss_val, acc_val, f1_score, precision, recall, fbetaprecisionskewed, fbetarecallskewed = myModel.evaluate(x_testNormalised, y_testCategorical)
 #   f1_score = precision = recall = fbetaprecisionskewed = fbetarecallskewed = 0
  #  loss_val, acc_val = myModel.evaluate(x_testNormalised, y_testCategorical)
    
    print('\nnAccuracy: ', acc_val)
    print('Loss: ', loss_val)
    print('F1 Score: ', f1_score)
    print('Precision: ', precision)
    print('Recall: ', recall)
    print('F- Beta (0.2) Score: ', fbetaprecisionskewed)
    print('F- Beta (2) Score: ', fbetarecallskewed)
    
    
    """ Saving results to csv file for analyse"""
    
    #
    # Results file layout:
    #
    #       1           2             3          4            5 
    # TRAING SIZE ; TEST SIZE ; RANDOM STATE; N. EPOCHS ; N. LAYERS CNN ;
    #
    #        6                    7                        8
    # TOTAL FILTERS CNN ; HIDDEN ACTIVATIONS CNN ; OUTPUT ACTIVATION CNN;
    #
    #       9                     10                11
    # LIST OF DROPOUTS CNN ; N. LAYERS FNN ; TOTAL NEURONS FNN; 
    #     
    #      12                        13                    14
    # HIDDEN ACTIVATIONS CNN ; OUTPUT ACTIVATIONS CNN; LIST OF DROPOUTS FNN
    #
    #      15             16            17           18          19
    # BATCH SIZE ; MIN DELTA ES ; PATIENCE ES ; METRIC ;       OPTMIZER ;
    #
    #     20              21             22          23        24
    # LEARNING RATE ; TYPE OF LOSS ;  LOSS VALUE ; ACCURACY ; F1 SCORE ; 
    #
    #   25        26           27          28
    # PRECISION ; RECALL ; F- BETA 0.2 ; F- BETA 2
    #
    
    contend = str(len(X)*myTestSize)
    contend += "," + str(myTestSize)
    contend += "," + str(MyRandomSt)
    contend += "," + str(noOfEpochs)
    contend += "," + str(noLayersCNN)
    contend += "," + str(noFiltersCNN + pow(noFiltersCNN,noLayersCNN))
    contend += "," + hiddenActCNN
    contend += "," + outputActCNN
    contend += "," + str(dropOutsCNN)
    contend += "," + str(noLayersFNN)
    contend += "," + str(noNeuronsFNN + pow(noNeuronsFNN,noLayersFNN))
    contend += "," + hiddenActFNN
    contend += "," + outputActFNN
    contend += "," + str(dropOutsFNN)
    contend += "," + str(myBatchSze)
    contend += "," + str(myMinDelta)
    contend += "," + str(myPatience)
    contend += "," + myMetric
    contend += "," + MyOptimizer
    contend += "," + str(MyLearnRate)
    contend += "," + MyLoss     
    contend += "," + str(loss_val)
    contend += "," + str(acc_val)
    contend += "," + str(f1_score)
    contend += "," + str(precision) 
    contend += "," + str(recall) 
    contend += "," + str(fbetaprecisionskewed) 
    contend += "," + str(fbetarecallskewed) 
    contend += "\n"
    
    saveToFile(myResults, contend)
    
    # Predicting aleatory sample from 0 to 10,000 (test set has 10,000 instances)
    someSample = random.randint(0, (len(X)*myTestSize) - 1 ) 
    y_predicted = np.argmax(myModel.predict(x_testNormalised), axis=-1)
    
    print("y_predicted for test dataset index ",someSample," is ", meta[b'label_names'][y_predicted[someSample]])
    
    # Print one image
    printImage(x_test[someSample])
   
    return myModel     
    
    
    
    
    
    
    
    
    

