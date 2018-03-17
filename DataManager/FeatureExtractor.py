import numpy as np
import zipfile
from Utilities.utilities import extractNIFTI
from DataManager.PreProcessData import *

class FeatureExtractor(object):
	""" Extracts features from a dataCollection

	Attrs
		option (string): what features to extract
		slice_ix (int): what slice to extract
		img_shape (int): size of the images
		sequence (int): how many subsequent slices to extract
	"""

	def __init__(self, option = 'image_and_k_space', slice_ix = 0.52, img_shape = 128, sequence = 1):
		self.option = option
		self.slice_ix = slice_ix
		self.img_shape = img_shape
		self.sequence = sequence

	def extractFeatureSet(self, subjects, dataset, filepath):
		if self.option is 'image_and_k_space':
			data_img_space, data_k_space = self.extractFeature_image_and_k_space(subjects, dataset, filepath)
			return data_img_space, data_k_space

		elif self.option is 'image_and_gibbs':
			data_img_gibbs, data_gibbs = self.extractFeature_image_and_gibbs(subjects, dataset, filepath)
			return data_img_gibbs, data_gibbs

		elif self.option is 'add_tumor':
			data_img, data_k_space, data_label = self.extractFeature_add_tumor(subjects, dataset, filepath)
			return {'image': data_img, 'k_space': data_k_space, 'label': data_label}

	def extractFeature_image_and_k_space(self, subjects, dataset, filepath, scan_type = 'T1'):
		# Count the number of valid brains in the dataset
		batch_size = 0
		for subject_id in subjects:
			zip_filename = filepath + str(subject_id) + '_3T_Structural_unproc.zip'
			if zipfile.is_zipfile(zip_filename): batch_size += 1
		print('Total subjects: ', batch_size)

		# Set containers in which to store the data
		data_k_space = np.zeros((self.sequence*batch_size, self.img_shape, self.img_shape), dtype=complex)
		data_img_space = np.zeros((self.sequence*batch_size, self.img_shape, self.img_shape), dtype=complex)

		# Extract the data
		batch_ix = 0
		for subject_id in subjects:
			zip_filename = filepath + str(subject_id) + '_3T_Structural_unproc.zip'
			if zipfile.is_zipfile(zip_filename):
				# Get the T1-weighted MRI image from the datasource and the current subject_id
				data, aff, hdr = extractNIFTI(filepath, subject_id, scan_type)
				for i in range(self.sequence):
					img, k_space_img = self.extract_image_and_k_space(data, self.slice_ix + i*0.003125)
					data_k_space[batch_ix] = k_space_img
					data_img_space[batch_ix] = img
					batch_ix += 1

					print('Subject ID: ', subject_id, '     Slice Index: ', self.slice_ix + i*0.003125)

		return data_img_space, data_k_space

	def extract_image_and_k_space(self, data, slice_ix):
		""" Extracts the image space and k-space data

		Args:
			data (3D numpy matrix): The volume image
			slice_ix (int): A number between [0, 1] detailing the slice to extract
		
		Returns:
			img: The complex image space
			k_space_img: The complex k-space
		"""
		# Extract the slice
		img = extractSlice(data, slice_ix)
		img = resizeImage(img, self.img_shape)
		phase_map = generate_synthetic_phase_map(self.img_shape)
		img = inject_phase_map(img, phase_map)
		k_space_img = transform_to_k_space(img)
		return img, k_space_img

	def extractFeature_image_and_gibbs(self, subjects, dataset, filepath, scan_type = 'T1'):
		# Count the number of valid brains in the dataset
		batch_size = 0
		for subject_id in subjects:
			zip_filename = filepath + str(subject_id) + '_3T_Structural_unproc.zip'
			if zipfile.is_zipfile(zip_filename): batch_size += 1
		print('Total subjects: ', batch_size)

		# Set containers in which to store the data
		data_img = np.zeros((self.sequence*batch_size, self.img_shape, self.img_shape), dtype=complex)
		data_img_gibbs = np.zeros((self.sequence*batch_size, self.img_shape, self.img_shape), dtype=complex)
		data_gibbs = np.zeros((self.sequence*batch_size, self.img_shape, self.img_shape), dtype=complex)

		# Extract the data
		batch_ix = 0
		for subject_id in subjects:
			zip_filename = filepath + str(subject_id) + '_3T_Structural_unproc.zip'
			if zipfile.is_zipfile(zip_filename):
				# Get the T1-weighted MRI image from the datasource and the current subject_id
				data, aff, hdr = extractNIFTI(filepath, subject_id, scan_type)
				for i in range(self.sequence):
					img, gibbs_img, gibbs = self.extract_image_and_gibbs(data, self.slice_ix + i*0.003125)
					data_img[batch_ix] = img
					data_img_gibbs[batch_ix] = gibbs_img
					data_gibbs[batch_ix] = gibbs
					batch_ix += 1

					print('Subject ID: ', subject_id, '     Slice Index: ', self.slice_ix + i*0.003125)

		return data_img_gibbs, data_gibbs

	def extract_image_and_gibbs(self, data, slice_ix):
		""" Extracts the image space and k-space data

		Args:
			data (3D numpy matrix): The volume image
			slice_ix (int): A number between [0, 1] detailing the slice to extract
		
		Returns:
			img: The complex image space
			k_space_img: The complex k-space
		"""
		# Extract the slice
		img = extractSlice(data, slice_ix)
		img = resizeImage(img, self.img_shape)
		gibbs_img = introduce_gibbs_artifact(img, 0.8)
		gibbs = gibbs_img - img
		return img, gibbs_img, gibbs

	def extractFeature_add_tumor(self, subjects, dataset, filepath, scan_type = 'T2'):
		# Count the number of valid brains in the dataset
		batch_size = 0
		for subject_id in subjects:
			zip_filename = filepath + str(subject_id) + '_3T_Structural_unproc.zip'
			if zipfile.is_zipfile(zip_filename): batch_size += 1
		print('Total subjects: ', batch_size)

		# Set containers in which to store the data
		data_shape = (self.sequence*batch_size, self.img_shape, self.img_shape)
		data_img = np.zeros(data_shape, dtype=complex)
		data_label = np.zeros((self.sequence*batch_size, 1,), dtype=int)
		data_k_space = []

		# Extract the data
		batch_ix = 0
		for subject_id in subjects:
			zip_filename = filepath + str(subject_id) + '_3T_Structural_unproc.zip'
			if zipfile.is_zipfile(zip_filename):
				# Get the T1-weighted MRI image from the datasource and the current subject_id
				data, aff, hdr = extractNIFTI(filepath, subject_id, scan_type)
				for i in range(self.sequence):
					img, k_space_img, label = self.extract_image_add_tumor(data, self.slice_ix + i*0.003125)

					data_img[batch_ix] = img
					data_k_space.append(k_space_img)
					data_label[batch_ix] = label
					batch_ix += 1

					print('Subject ID: ', subject_id, '     Slice Index: ', self.slice_ix + i*0.003125)
		return data_img, np.asarray(data_k_space), data_label

	def extract_image_add_tumor(self, data, slice_ix):
		""" Extracts the image space and k-space data

		Args:
			data (3D numpy matrix): The volume image
			slice_ix (int): A number between [0, 1] detailing the slice to extract
		
		Returns:
			img: The complex image space
			k_space_img: The complex k-space
		"""
		# Extract the slice
		img = extractSlice(data, slice_ix)
		img = resizeImage(img, self.img_shape)

		label = np.random.randint(0,2)
		if label == 1:
			img = add_tumor(img)

		#phase_map = generate_synthetic_phase_map(self.img_shape)
		#img = inject_phase_map(img, phase_map)
		k_space_img = transform_to_k_space(img, acquisition = 'radial', sampling_percent = 0.5)
		return img, k_space_img, label