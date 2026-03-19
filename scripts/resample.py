import os
import numpy as np
import SimpleITK as sitk
import argparse
# from utils_post import resample

# python resample.py --input test_scaled.nii.gz --output test_resampled.nii.gz

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, required=True, help="Path to the input image")
parser.add_argument("--output", type=str, required=True, help="Path to save the resampled image")
parser.add_argument("--new_size", type=int, nargs=3, default=[128, 128, 128], metavar="x,y,z", help="Target output shape for resampling (width height depth)")        
parser.add_argument("--interpolator", type=str, default="hamming", help="Interpolator type for resampling (nearest, linear, bspline, hamming, cosine, lanczos)")
args = parser.parse_args()

# Interpolators mapping for resampling
INTERPOLATORS = {
    "nearest": sitk.sitkNearestNeighbor,
    "linear": sitk.sitkLinear,
    "bspline": sitk.sitkBSpline3,
    "hamming": sitk.sitkHammingWindowedSinc,
    "lanczos": sitk.sitkLanczosWindowedSinc,
    "gaussian": sitk.sitkGaussian,
    "cosine": sitk.sitkCosineWindowedSinc
}

def resample(image, new_size=(256, 256, 256), interpolator_type="hamming"):
    """
    Resample the image to a new size while preserving physical dimensions.
    Spacing is automatically calculated to maintain the same physical size

    Args:
    -----
    image : sitk.Image
        The input image to be resampled
    new_size : tuple
        The desired size of the output image (width, height, depth)
    interpolator_type : str
        The type of interpolator to be used for resampling (default is "hamming")

    Returns:
    -------
        resampled_image : sitk.Image
            The resampled image with the specified size and automatically calculated spacing
    """

    # Interpolator
    interpolator = INTERPOLATORS[interpolator_type]

    # Get original properties
    original_size = image.GetSize()
    original_spacing = image.GetSpacing()
    original_direction = image.GetDirection()
    original_origin = image.GetOrigin()
    
    # Calculate spacing to preserve physical size for each dimension
    new_spacing = tuple(
        original_size[i] * original_spacing[i] / new_size[i] 
        for i in range(3)
    )

    # Define resampler
    resampler = sitk.ResampleImageFilter()
    resampler.SetInterpolator(interpolator)
    resampler.SetOutputSpacing(new_spacing)
    resampler.SetSize(new_size)
    resampler.SetOutputDirection(original_direction)
    resampler.SetOutputOrigin(original_origin)
    resampler.SetTransform(sitk.Transform())
    resampler.SetDefaultPixelValue(0)

    # Resample
    resampled_image = resampler.Execute(image)  

    return resampled_image

if __name__ == "__main__":
    # Read image
    input_image = sitk.ReadImage(args.input)

    # Resample image to the specified size
    resampled_image = resample(input_image, new_size=args.new_size, interpolator_type=args.interpolator)

    # Save resampled image
    sitk.WriteImage(resampled_image, args.output)