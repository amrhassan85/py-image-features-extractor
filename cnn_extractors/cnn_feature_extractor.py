import csv
import os

import numpy as np
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.preprocessing import image


class FeatureExtractor:
  def __init__(self, base_route, model_name, output_route):
    self.bath_size = 128
    self.width = self.height = 75
    self.image_shape = (self.width, self.height, 3)
    
    self.output_route = output_route
    self.model_name = model_name
    self.train_route = base_route + "/train"
    
    self.labels = None
    self.features = None
    self.directory_iterator = None
  
  def get_directory_iterator(self, route):
    image_generator = image.ImageDataGenerator(rescale=1.0 / 255)
    
    self.directory_iterator = image_generator.flow_from_directory(
      directory=route,
      target_size=(self.width, self.height),
      batch_size=self.bath_size,
      class_mode=None,
      shuffle=False
    )
  
  def get_model(self):
    if self.model_name is "inception":
      return InceptionV3(include_top=False, weigths="imagenet", input_shape=self.image_shape)
  
  def get_features(self, model):
    model = model.compile(optimizer="adagrad", loss="categorical_crossentropy", metrics=["accuracy"])
    self.features = model.predict_generator(self.directory_iterator)
  
  def get_labels(self, folder, directory_iterator):
    dictionary_labels = {}
    for label, folder in enumerate(os.listdir(folder)):
      dictionary_labels[folder] = label
    
    self.labels = np.array(
      [FeatureExtractor.__get_label_from_file__(f, dictionary_labels) for f in directory_iterator.filenames])
  
  def save_csv(self):
    features_list = [i for i in range(self.features.shape[-1])]
    features_list.append(-1)
    
    with open(self.output_route, 'w') as f:
      writer = csv.writer(f)
      
      writer.writerow(features_list)
      for i in range(self.features.shape[0]):
        features = self.features[i][0][0]
        features = np.append(features, [self.labels[i]])
        
        writer.writerow(features)
  
  def extract(self):
    self.get_directory_iterator(self.train_route)
    self.get_labels(self.train_route, self.directory_iterator)
    self.get_features(self.get_model())
    self.save_csv()
  
  @staticmethod
  def __get_label_from_file__(file_name, dictionary_labels):
    return dictionary_labels[file_name.split("/")[0]]