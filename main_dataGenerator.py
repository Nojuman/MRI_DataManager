import numpy as np 
import h5py
from DataManager.DataManager import DataManager
from Utilities.utilities import extract_NIFTI, extract_FigShare
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from DataManager.FeatureExtractor import *

'''
#Example to extract FigShare Dataset
dataManager = DataManager(r'C:/Users/eee/workspace_python/Image Reconstruction/data/', ['FigShare'])
params = {'database_name': 		'fig_share_data',
		  'dataset': 			'FigShare',
		  'feature_option':		'image_and_k_space',
		  'img_shape': 			128,
		  'num_subjects': 		'all'}

print(len(dataManager.dataCollection['FigShare']))
print(len(dataManager.data_splits['FigShare'][0]))
print(len(dataManager.data_splits['FigShare'][1]))
print(len(dataManager.data_splits['FigShare'][2]))

dataManager.compile_dataset(params)
'''

# Example to extract data from the ADNI dataset
dataManager = DataManager(r'C:/Users/eee/workspace_python/Image Reconstruction/data/', ['ADNI'])

#Example to extract BRATS Dataset
# dataManager = DataManager(r'C:/Users/eee/workspace_python/Image Reconstruction/data/', ['BRATS'])

# params = {'database_name': 		'brats_data',
# 		  'dataset': 			'BRATS',
# 		  'feature_option':		'image_and_k_space',
# 		  'img_shape': 			128,
# 		  'num_subjects': 		'all',
# 		  'slice_ix': 			0.52,
# 		  'consec_slices':		30,
# 		  }




#print(dataManager.getData('ADNI', 'Subject'))
#print(dataManager.getKeys('ADNI'))
#coll = dataManager.getDataCollection()

#dataManager.viewSubject('ADNI', 100206)

#print(dataManager.dataCollection['ADNI']['Subject'])

#print(dataManager.data_splits['ADNI'][2].shape)

#dataManager.compileDataset('data', 'ADNI', option = 'image_and_k_space', slice_ix = 0.52, img_shape = 128)

#dataManager.compileDataset('data_gibbs', 'ADNI', option = 'image_and_gibbs', slice_ix = 0.52, img_shape = 128)


params = {'database_name': 		'data_tumor_TEST',

		  'dataset': 			'ADNI',
		  'feature_option':		'add_tumor',
		  'slice_ix': 			0.52, #0.32, #0.52,
		  'img_shape': 			128,
		  'consec_slices':		30, #120,#30,
		  'num_subjects': 		'all',
		  'scan_type': 			'T2',
		  'acquisition_option':	'radial',
		  'sampling_percent': 	0.01,
		  'accel_factor':       0, # How to implement this?
		  'tumor_option':		'circle',
		  'tumor_radius':       0.05,
		  'tumor_radius_range': [0.8,2.2],
		  'distort_mult_range': [0.5,1.5]}

dataManager.compile_dataset(params)

data = {}
hf = h5py.File('experiments/data_tumor_cross.h5', 'r')
print([key for key in hf.keys()])
for key in hf.keys():
	print(key)
	vals = list(hf[key])
	data.update({key: np.asarray(vals)})
hf.close()

print(list(data.keys()))

for d in list(data.keys()):
	print(d, data[d].shape)


ix = 0
'''
print('Label = ', data['train_label'][ix])
plt.subplot(2,1,1)
plt.imshow(np.abs(data['train_image'][ix]).T, cmap = 'gray')
plt.subplot(2,1,2)
plt.imshow(np.log(np.abs(data['train_k_space'][ix])).T, cmap = 'gray')
plt.show()
'''

plt.subplot(1,2,1)
plt.imshow(np.abs(np.rot90(data['train_image'][ix])), cmap = 'gray')
plt.subplot(1,2,2)
plt.imshow(np.abs(np.rot90(data['train_k_space'][ix])), cmap = 'gray')
plt.show()


'''
plt.subplot(2,2,1)
plt.imshow(np.abs(np.rot90(data['train_image'][ix])), cmap = 'gray')
plt.subplot(2,2,2)
plt.imshow(np.abs(np.rot90(data['train_image'][(ix + params['consec_slices'] - 1)//3])), cmap = 'gray')
plt.subplot(2,2,3)
plt.imshow(np.abs(np.rot90(data['train_image'][2*(ix + params['consec_slices'] - 1)//3])), cmap = 'gray')
plt.subplot(2,2,4)
plt.imshow(np.abs(np.rot90(data['train_image'][ix + params['consec_slices'] - 1])), cmap = 'gray')
plt.show()
'''


'''
from copy import deepcopy

filepath = r'C:/Users/eee/workspace_python/Image Reconstruction/data/ADNI/MRI data/'
data, aff, hdr = extract_NIFTI(filepath, 100206, 'T2')
#data = data[:,:,180]

slice_ix = 180*0.003125
img = extract_slice(data, slice_ix)
img = resize_image(img, img.shape[0])

img_tumor = add_tumor(deepcopy(img))

phase_map = generate_synthetic_phase_map(img.shape[0])
img = inject_phase_map(img, phase_map)
k_space_img = transform_to_k_space(img)

plt.figure()
plt.subplot(2,2,1)
plt.imshow(np.abs(img/np.max(img)).T, cmap = 'gray')
plt.axis('off')
plt.colorbar()
plt.subplot(2,2,2)
plt.imshow(np.abs(k_space_img/np.max(k_space_img)).T, cmap = 'gray')
plt.axis('off')
plt.colorbar()

phase_map = generate_synthetic_phase_map(img_tumor.shape[0])
img_tumor = inject_phase_map(img_tumor, phase_map)
k_space_img = transform_to_k_space(img_tumor)

plt.subplot(2,2,3)
plt.imshow(np.abs(img_tumor/np.max(img_tumor)).T, cmap = 'gray')
plt.axis('off')
plt.colorbar()
plt.subplot(2,2,4)
plt.imshow(np.abs(k_space_img/np.max(k_space_img)).T, cmap = 'gray')
plt.axis('off')
plt.colorbar()
plt.show()
'''