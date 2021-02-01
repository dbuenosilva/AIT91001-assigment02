#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anomalies Detection on images
Date: 24/01/2021
Author: Diego Bueno (ID: 23567850) / Isabelle Sypott (ID: 21963427 )
e-mail: d.bueno.da.silva.10@student.scu.edu.au / i.sypott.10@student.scu.edu.au



 it has been changed ok


"""

## importing the libraries required
import numpy as np
import pathlib
import pickle
import random
import matplotlib.pyplot as plt
import tensorflow as tf # using Tensorflow 2.4
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split #used to split data into training and test segments
from keras.callbacks import EarlyStopping, ModelCheckpoint 
from tensorflow import keras #keras is the api that provides functionality to work with tensorflow
from keras.preprocessing.image import ImageDataGenerator


""" Function read( )

    Read a pickle file format  
    and return a Python dictionary with its content.

    parameters: file_name

    return: 
        dict: a dictionary with the content encoding in bytes
    
"""
def read(file_name):
    with open(file_name, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

# initialising variables
epochs    = 2
test_size = 0.2
number_of_batch_files = 5
data      = [] # array with all images read from batch files
X         = [] # array with images data including channels (RGB)
y         = [] # array with labels (index of category of images)

# Loading data 
# images/ folder should be in the same location of the script
# Getting the relative path of the file to avoid MacOS issues
path = pathlib.Path(__file__).resolve().parent
path = str(path) + "/"

## data: data_batch_N dictionary
    # { 
    # b'labels': b'training batch 5 of 5' => title of dictionary
    # b'labels': [1, 8... n ] => array 1D of size 10,000 labels
    # b'data': array([[255, 252, 253,..] , [127, 126, 127, ...], [...]] ) => array of size 10,000 x 3,072 ( 1024 R + 1024 G + 1024 B )
    # b'filenames': [b'compact_car_s_001706.png', b'icebreaker_s_001689.png',...] => array of size 10,000 with files names
    # }    
for n in range(1,number_of_batch_files + 1,1):
    data = np.append(data, read( path + 'images/data_batch_' + str(n)) )

## meta dictionary:
    # {   
    # num_cases_per_batch': 10000
    #                      0           1            2       3        4       5        6        7         8         9
    # label_names': [b'airplane', b'automobile', b'bird', b'cat', b'deer', b'dog', b'frog', b'horse', b'ship', b'truck']
    # b'num_vis':    3072 ( 1024 R + 1024 G + 1024 B )   
    # } 
meta = read( path + 'images/batches.meta')

# Unifying all images pixels values in unique array X
for images in data:
    if len(X) == 0:
        X = images[b'data']
    else:
        X = np.concatenate((X, images[b'data']), axis=0) 
    y = np.append(y, images[b'labels'] )
    
    
print("\nX.shape with all images data: ", X.shape)
print("\ny.shape with all images labels", y.shape)

# Selecting 40000 instances for training set and 10000 for test set
[x_train, x_test, y_train, y_test] = train_test_split(X, y, test_size = test_size, random_state= 42 )
    
## Shape of original data
print("\n\nx_train initial shape:  ", x_train.shape)
print("x_test initial shape:  ", x_test.shape)
print("y_train initial shape:  ", len(y_train))
print("y_test initial shape:  ", len(y_test))
print("\n")

# Pre-processing
## Loading/Reading the required data for analysis & also preprocessing data.  
### Zoom range is randomly zooming into images, horizontal flip randomly flips half images horizontally, shear range randomly shears some images - helps give detail to images that are blurry or fragmented in some way
#x_trainNormalised = x_train(rescale = 1./255, shear_range = 0.1, zoom_range = 0.1,horizontal_flip = True)
#x_testNormalised = x_test(rescale = 1./255, shear_range = 0.1, zoom_range = 0.1,horizontal_flip = True)

#x_trainNormalised = ImageDataGenerator(rescale = 1./255, shear_range = 0.1, zoom_range = 0.1,horizontal_flip = True)
#x_testNormalised = ImageDataGenerator(rescale = 1./255, shear_range = 0.1, zoom_range = 0.1,horizontal_flip = True)

# Pre-processing
x_trainNormalised = x_train / 255.0
x_testNormalised = x_test / 255.0

## Changing the shape of INPUT data
nInstancesTrain  = x_trainNormalised.shape[0]
nInstancesTest   = x_testNormalised.shape[0]
nRowns           = 32 
nColumns         = 32
nChannels        = 3  # 3 channels denotes one red, green and blue (RGB image)

#x_train = x_trainNormalised.reshape(8000, 32, 32, 3)
x_trainNormalised = x_trainNormalised.reshape(nInstancesTrain, nRowns, nColumns, nChannels) 

#x_test = x_test.x_testNormalised(2000, 32, 32, 3)
x_testNormalised = x_testNormalised.reshape(nInstancesTest, nRowns, nColumns, nChannels)

## Changing the shape of OUTPUT layer, also changing the labels of train and test into categorical data
# It creates hot vectors for the classes like: [0. 0. 0. 1. 0. 0. 0. 0. 0. 0.]
y_trainCategorical = to_categorical(y_train)
y_testCategorical = to_categorical(y_test)

# Checking that train and test data categorical and normalised are the correct shape for NN
print("x_train normalised shape: ", x_trainNormalised.shape)
print("x_test normalised shape: ", x_testNormalised.shape)
print("y_trainCategorical shape: ", y_trainCategorical.shape)
print("y_testCategorical shape: ", y_testCategorical.shape)



# designing the Convolutional Neural Network 
model = tf.keras.models.Sequential()
                                                                                 #32    #32        #3           
model.add(tf.keras.layers.Conv2D(filters=32, kernel_size=(3,3), input_shape = (nRowns, nColumns, nChannels), activation='relu')) #layer 1

# Size of Pooling of 2x2 is default for images
model.add(tf.keras.layers.MaxPooling2D(pool_size = (2, 2)))
model.add(tf.keras.layers.Conv2D(filters=64, kernel_size=(3,3), activation='relu')) # layer 2
model.add(tf.keras.layers.MaxPool2D(pool_size = (3,3)))

model.add(tf.keras.layers.Dropout(0.25))

# Classifing by Fully Connect Neural Network
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(128, activation='relu'))
#model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(10, activation='softmax'))

## compile CNN => not sparse_categorical_crossentropy because classes are exclusives!
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

## validate
model.fit(x_trainNormalised, y_trainCategorical, epochs=epochs, batch_size=32,  verbose=1)

## evaluating the accuracy using test data
loss_val, acc_val = model.evaluate(x_testNormalised, y_testCategorical)
print('Accuracy is: ', acc_val)

## evaluating the accuracy another way to ensure its accurate - with a for loop

#Rec_Acc = 0

#for i in range(len(y_test)):

#  if (y_predicted[i] == y_test[i]):

    #Rec_Acc = Rec_Acc +1

  # else:

  #   print(y_predicted[i][0])   


#Rec_Acc = Rec_Acc/len(y_test)*100

#print("Recognition Accuracy: ",Rec_Acc,"%")



# Predicting aleatory sample from 0 to 2000 (test set has 2000 instances)
someSample = random.randint(0, (len(X)*test_size) - 1 ) 

y_predicted = np.argmax(model.predict(x_testNormalised), axis=-1)
#y_predicted = model.predict_classes(x_testNormalised) ==> DEPRECATED

print("y_predicted for test dataset index ",someSample," is ", meta[b'label_names'][y_predicted[someSample]])

im_r = x_test[someSample][0:1024].reshape(32, 32)
im_g = x_test[someSample][1024:2048].reshape(32, 32)
im_b = x_test[someSample][2048:3072].reshape(32, 32)

img = np.dstack((im_r, im_g, im_b))

plt.imshow(img) 
plt.show()
