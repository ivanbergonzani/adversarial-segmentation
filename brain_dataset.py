import scipy.io
import numpy as np
import h5py

import cv2
import os

# cjdata.label: 1 for meningioma, 2 for glioma, 3 for pituitary tumor
# cjdata.PID: patient ID
# cjdata.image: image data
# cjdata.tumorBorder: a vector storing the coordinates of discrete points on tumor border.
# 		For example, [x1, y1, x2, y2,...] in which x1, y1 are planar coordinates on tumor border.
# 		It was generated by manually delineating the tumor border. So we can use it to generate
# 		binary image of tumor mask.
# cjdata.tumorMask: a binary image with 1s indicating tumor region


raw_dataset_path = "brainTumorDataPublic"
new_dataset_path = "brain_tumor_dataset"
mask_dataset_path = "brain_mask_dataset"

splitted_healthy_path = "dataset/brain_tumor_dataset_splitted/0"
splitted_tumor_path = "dataset/brain_tumor_dataset_splitted/1"
splitted_tumor_mask_path = "dataset/brain_tumor_dataset_splitted/mask"



def load_brain_dataset():

	H = list()
	for image_name in os.listdir(splitted_healthy_path):
		image_path = os.path.join(splitted_healthy_path, image_name)
		image = cv2.imread(image_path)
		H.append(image)
		
	T = list()
	for image_name in os.listdir(splitted_tumor_path):
		image_path = os.path.join(splitted_tumor_path, image_name)
		image = cv2.imread(image_path)
		if image is None:
			continue
		T.append(image)
		
	return np.array(H), np.array(T)



if __name__ == "__main__":
    file_names = os.listdir(raw_dataset_path)

    for file_name in file_names:

        file_path = os.path.join(raw_dataset_path, file_name)
        file = h5py.File(file_path, 'r')

        # extract image and classification data
        label = np.array(file.get("cjdata/label"))[0,0]
        image = np.array(file.get('cjdata/image'))
        borders = np.array(file.get('cjdata/tumorBorder'))

        if image.shape != (512,512):
            continue

        # process image
        image = 255 * (image / image.max())

        # mask creation and image subdivision
        borders = np.reshape(borders, (-1,2))
        borders = borders[:,::-1]
        borders_x = borders[:,0]
        borders_y = borders[:,1]

        mask = np.zeros( image.shape ) # create a single channel 200x200 pixel black image
        cv2.fillPoly(mask, pts=np.array([borders], dtype=np.int32), color=(255,255,255))

        # save image in folder depending on label
        image_name = file_name[:-3] + "png"
        upper_name = file_name[:-4] + "u.png"
        lower_name = file_name[:-4] + "l.png"

        output_folder = os.path.join(new_dataset_path, str(label))
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        output_path = os.path.join(output_folder, image_name)
        cv2.imwrite(output_path, image)

        # save mask
        mask_output_folder = os.path.join(mask_dataset_path, str(label))
        if not os.path.isdir(mask_output_folder):
            os.makedirs(mask_output_folder)
        mask_path = os.path.join(mask_output_folder, image_name)
        cv2.imwrite(mask_path, mask)


        # split images in half and classify based on healty or tumor
        upper_has_tumor = False
        lower_has_tumor = False

        if np.min(borders_y) < 250:
            upper_has_tumor = True
        if np.max(borders_y) >= 250:
            lower_has_tumor = True

        upper = image[:256,:]
        lower = image[256:,:]
        lower = lower[::-1,:]

        upper_mask = mask[:256,:]
        lower_mask = mask[256:,:]
        lower_mask = lower_mask[::-1,:]

        if not os.path.isdir(splitted_tumor_path):
            os.makedirs(splitted_tumor_path)
        if not os.path.isdir(splitted_healthy_path):
            os.makedirs(splitted_healthy_path)
        if not os.path.isdir(splitted_tumor_mask_path):
            os.makedirs(splitted_tumor_mask_path)

        if upper_has_tumor:
            cv2.imwrite(os.path.join(splitted_tumor_path, upper_name), upper)
            cv2.imwrite(os.path.join(splitted_tumor_mask_path, upper_name), upper_mask)
        else:
            cv2.imwrite(os.path.join(splitted_healthy_path, upper_name), upper)

        if lower_has_tumor:
            cv2.imwrite(os.path.join(splitted_tumor_path, lower_name), lower)
            cv2.imwrite(os.path.join(splitted_tumor_mask_path, lower_name), lower_mask)
        else:
            cv2.imwrite(os.path.join(splitted_healthy_path, lower_name), lower)






#