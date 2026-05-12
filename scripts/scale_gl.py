import os
import numpy as np
import SimpleITK as sitk
import argparse
# from utils_post import scale_GL

# python scale_gl.py --input 141_S_0853_sampled_CN_26.nii.gz  --output test_scaled.nii.gz --label "CN"

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, required=True, help="Path to the input image")
parser.add_argument("--output", type=str, required=True, help="Path to save the scaled image")
#parser.add_argument("--label", type=str, required=True, help="Diagnosis label for reverse clipping (0=CN, 1=MCI, 2=AD)")
args = parser.parse_args()

# Rarget ranges obtained from original dataset: mean of 1st and 99th percentiles per diagnosis label
CLIP_TARGET = {
    "CN": (0.0, 236.303704), #CN 236.3037037037037
    "MCI": (0.0, 233.552791), #MCI 233.5527911877324
    "AD": (0.0, 235.752294)   #AD 235.75229357798165
}

def scale_GL(image, min_val, max_val):
    """
    Reverse preprocessing by mapping from any normalized range back to original clipped intensity range.

    Args:
    -----
    image : sitk.Image
        The input image (can be in any range, e.g., -1 to 1, 0 to 1, etc.)
    min_val : float
        The target minimum value for intensity scaling
    max_val : float
        The target maximum value for intensity scaling

    Returns:
    -------
        scaled_image : sitk.Image
            The scaled image with pixel values in the range [min_val, max_val]
    """

    array = sitk.GetArrayFromImage(image)

    img_min = np.min(array)
    img_max = np.max(array)

    # Avoid division by zero :(
    if img_max - img_min == 0:
        # Set to target low percentile
        scaled_image = np.full_like(array, min_val)
    else:
        # Map from any input range directly to the clipped intensity range
        scaled_image = (array - img_min) / (img_max - img_min) * (max_val - min_val) + min_val
    
    scaled_image = sitk.GetImageFromArray(scaled_image)
    scaled_image.CopyInformation(image)

    return scaled_image

if __name__ == "__main__":
    # Read image
    input_image = sitk.ReadImage(args.input)

    # Extract label from filename (assuming format: <ID>_subject_<CN/MCI/AD>_<...>.nii.gz)
    filename = os.path.basename(args.input)
    label = None
    for diagnosis in CLIP_TARGET.keys():
        if diagnosis in filename:
            label = diagnosis
            break

    if label is None:
        raise ValueError(
            f"Label not found in filename: {filename}. Expected one of {list(CLIP_TARGET.keys())}."
        )

    # Extract targets lower and upper percentiles for reverse clipping
    p_low_target, p_high_target = CLIP_TARGET[label]#[args.label]

    # Scale the image to the specified range
    scaled_image = scale_GL(input_image, p_low_target, p_high_target)

    # Save scaled image
    sitk.WriteImage(scaled_image, args.output)