import os
import numpy as np
import tomopy
import matplotlib.pyplot as plt
from skimage import io
from skimage import exposure
import tifffile as tiff
from mayavi import mlab

def read_projections(folder_path):
    # List all TIFF files in the folder
    files = sorted([f for f in os.listdir(folder_path) if f.endswith('.tif')])
    if not files:
        raise ValueError("No TIFF files found in the specified folder.")

    # Read the first image to determine the shape
    first_image = tiff.imread(os.path.join(folder_path, files[0]))
    num_projections = len(files)
    image_shape = first_image.shape

    # Initialize an array to hold all projections
    projections = np.zeros((num_projections, *image_shape), dtype=np.float32)

    # Read each image
    for i, file in enumerate(files):
        img = tiff.imread(os.path.join(folder_path, file))
        projections[i] = img

    return projections

# Step 1: Read projection images from a folder
input_folder = 'D:\BatteryCT\data\scan1'
projections = read_projections(input_folder)

# Step 2: Generate angles for projections (assuming uniformly spaced angles)
num_projections = projections.shape[0]
theta = np.linspace(0, 2*np.pi, num_projections)

# Step 3: Reconstruct the image using Filtered Back Projection (FBP)
reconstruction = tomopy.recon(projections, theta, algorithm='gridrec')

# Step 4: Save the reconstructed slices as a TIFF image stack
output_dir = 'reconstruction_output_1'
os.makedirs(output_dir, exist_ok=True)

for i in range(reconstruction.shape[0]):
    # Normalize the image for better visualization and save
    slice_img = exposure.rescale_intensity(reconstruction[i], out_range=(0, 1))
    tiff.imsave(f"{output_dir}/slice_{i:04d}.tiff", slice_img.astype(np.float32))

# Step 5: Visualize the reconstruction results
def plot_reconstruction(projections, reconstruction):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(projections[:, int(projections.shape[1] / 2)], cmap='gray')
    axes[0].set_title('Projections')
    axes[1].imshow(projections[:, :, int(projections.shape[2] / 2)], cmap='gray')
    axes[1].set_title('Single Projection')
    axes[2].imshow(reconstruction[int(reconstruction.shape[0] / 2)], cmap='gray')
    axes[2].set_title('Reconstruction')
    for ax in axes:
        ax.axis('off')
    plt.tight_layout()
    plt.show()

plot_reconstruction(projections, reconstruction)


# Step 6: 3D Visualization with threshold and slicing options
def visualize_3d(volume, threshold=None, z_slice=None):
    mlab.figure(size=(800, 800), bgcolor=(1, 1, 1))
    
    # Apply threshold if provided
    if threshold is not None:
        volume = np.where(volume >= threshold, volume, 0)
    
    src = mlab.pipeline.scalar_field(volume)
    
    # Slice through the z direction if provided
    if z_slice is not None:
        mlab.pipeline.image_plane_widget(src, plane_orientation='z_axes', slice_index=z_slice)
    else:
        mlab.pipeline.volume(src, vmin=volume.min(), vmax=volume.max())
    
    mlab.axes()
    mlab.show()

# Example usage:
# Set a threshold for grey values
threshold_value = 0.1

# Slice index in the z-direction (None for no slicing)
z_slice_index = 50

visualize_3d(reconstruction, threshold=threshold_value, z_slice=z_slice_index)
