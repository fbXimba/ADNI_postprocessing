import os
import numpy as np
import SimpleITK as sitk
import pandas as pd

df = pd.read_csv("../tesi/ADNI_processed_FS/final_subjects_CN.csv")
data_dir = "../tesi/ADNI_processed_FS/processed_images"
p_low=0.01
p_high=99.99


if __name__ == "__main__":
    # read diagnosis groups 

    for diagnosis in df['Group'].unique():
        # select all images with the current diagnosis: if file name contains diagnosis, add to group
        
        #file_pattern = f"*{diagnosis}*.nii.gz" per file generati

        subjects = df[df['Group'] == diagnosis]['Subject'].tolist()
        all_low = []
        all_high = []
        for subject in subjects:
            file_path = os.path.join(data_dir, subject, f"{subject}_brain_resampled.nii.gz")
            if os.path.exists(file_path):
                img = sitk.ReadImage(file_path)
                array = sitk.GetArrayFromImage(img)
                # Calculate the percentiles for the current image
                all_low.append(np.percentile(array, p_low))
                all_high.append(np.percentile(array, p_high))
                
            else:
                print(f"File not found: {file_path}")

        # Calculate the mean target percentiles for the current diagnosis 
        p_low_target = np.mean(all_low)
        p_high_target = np.mean(all_high)

        #p_low_target, p_high_target = piangere(group, diagnosis)
        print(f"Diagnosis: {diagnosis}, subjects: {len(subjects)}, p_low_target: {p_low_target}, p_high_target: {p_high_target}")
   