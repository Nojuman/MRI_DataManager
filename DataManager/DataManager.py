import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from DataManager.utilities import extractNIFTI, readCSV, write_data
from DataManager.PreProcessData import *
from DataManager.FeatureExtractor import *
import numpy as np

class DataManager(object):
	""" Organization of the data

	The class contains a dictionary with the metadata of all the datasets that we will be using.
	It is a means to organize and aggregate data from different sources. It is also used as a wrapper to
	fetch the data from these different sources and combine them.

	Attrs:
		dataCollection (dictionary): Contains the metadata for all the datasets stored indexed by 
		                             the name of the dataset.
		data_splits (dictionary): Contains the train/validation/test indices for each of the 
		                          datasets in dataCollection.
		information (dictionary): Contains information about the dataset 
		                          [0]: filepath to the metadata
		                          [1]: filepath to the data*
		                          [2]: indices to extract in the metadata
		                          [3]: key for the index in the dataset

		                          * filepath (string): Filepath to the root folder where datasets stored
		                   		  Requried file structure
		                      		- filepath
		                         		- ADNI (folder)
		                            		- MRI data (folder): contains the NIFTI files
		                            		- dataset_metadata.csv: file comtaining metadata
	"""

	def __init__(self, filepath, datasets = None):
		self.dataCollection = {}
		self.data_splits = {}

		# Information about the datasets as a dictionary
		self.information = {'ADNI': [filepath + 'ADNI/dataset_metadata.csv', 
									 filepath + r'ADNI/MRI data/', 
									 [0, 3, 4, 6],
									 'Subject']}
		# Add the datasets that are listed to the data collection
		self.addDatasets(datasets)

	def addDatasets(self, datasets):
		""" Add new datasets to the dataCollection dictionary

		Args:
			datasets (list of strings): List of strings with the name of all the datasets
										to add to the collection.
		"""
		for dataset in datasets:
			filepath = self.information[dataset][0]
			indices = self.information[dataset][2]
			key = self.information[dataset][3]
			# Add dataset to the collection
			self.dataCollection.update({str(dataset): readCSV(filepath, indices)})
			self.train_validate_test_split(dataset, key)

	def train_validate_test_split(self, dataset, column_header, train_percent=.6, valid_percent=.2, seed=None):
		"""Splits up the index associated with the dataset into a train/validation/test set
		
		Adds a new train/validation/test set to the data_splits dictionary.

		Args:
			dataset (string): Name of the dataset in question
			column_header (string): Name of the column header with the index
			train_percent (float): percentage of the data to reserve for training [0, 1]
			valid_percent (float): percentage of the data for validation [0, 1]
			seed (int): means by which to generate the random shuffling of the data
		"""
		if not seed is None: np.random.seed(seed)
		
		data = self.dataCollection[dataset][column_header]
		perm = np.random.permutation(data)
		m = len(data)

		# Get the split indices
		train_end = int(train_percent * m)
		valid_end = int(valid_percent * m) + train_end
		train, valid, test = perm[:train_end], perm[train_end:valid_end], perm[valid_end:]

		self.data_splits.update({str(dataset): [train, valid, test]})


	def compileDataset(self, database_name, dataset, option = 'image_and_k_space', slice_ix = 0.52, img_shape = 128):
		""" Extracts the features for the datasets and compiles them into a database

		Args:
			dataset (string): the dataset from which to extract features. 
			option (string): Option for determining what features to extract
							 - 'image_and_k_space': generate a database with image space and k-space

		"""
		# Extract features 
		featureExtractor = FeatureExtractor(option, slice_ix = slice_ix, img_shape = img_shape, sequence = 3)

		filepath = self.information[dataset][1]

		# Description of the dataset that is being generated
		attributes = {'option': option, 
					  'dataset': dataset, 
					  'slice_ix': slice_ix, 
					  'img_size': img_shape}

		# Generate the databases
		databases = {}
		for ix, i in enumerate(['train', 'validation', 'test']):
			subjects = self.data_splits[dataset][ix]
			features, targets = featureExtractor.extractFeatureSet(subjects[0:2], dataset, filepath)
			databases.update({'X_'+i: features, 'Y_'+i: targets})

		# Write the datasets to the .h5 database file
		write_data(databases, attributes, database_name)

	def getDataCollection(self):
		return self.dataCollection

	def getData(self, dataset, key):
		if dataset in self.dataCollection:
			if key in self.dataCollection[dataset].columns:
				return self.dataCollection[dataset][key]

	def getKeys(self, dataset):
		if dataset in self.dataCollection:
			return self.dataCollection[dataset].keys()

	def viewSubject(self, dataset, subject_id, slice_ix = 0.5):
		filepath = self.information[dataset][1]

		# Get the T1-weighted MRI image from the datasource and the current subject_id
		data, aff, hdr = extractNIFTI(filepath, subject_id)
		img = extractSlice(data, slice_ix)
		plt.imshow(img.T, cmap = 'gray')
		plt.colorbar()
		plt.show()