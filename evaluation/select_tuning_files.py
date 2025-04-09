'''Script to randomly select the 20% of the instances for the algorithm tuning process'''
import os
import random
import shutil


def randomly_select_files(src_dir, dest_dir, num_files=8):
    # Ensure source directory exists
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"The source directory '{src_dir}' does not exist.")

    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Get the list of all files in the source directory
    all_files = [
        file for file in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, file))]

    # Check if there are enough files in the source directory
    if len(all_files) < num_files:
        raise ValueError(f"Not enough files in '{src_dir}' to select {num_files}.")

    # Randomly select the specified number of files
    selected_files = random.sample(all_files, num_files)

    # Copy the selected files to the destination directory
    for file in selected_files:
        shutil.copy(os.path.join(src_dir, file), os.path.join(dest_dir, file))

    print(f"Successfully copied {num_files} files to '{dest_dir}'.")


# Example usage
path = os.path.join('instances', 'GDP')

subdirs = os.listdir(path)
for dir in subdirs:
    src_directory = os.path.join(path, dir)
    dest_directory = os.path.join('instances', 'GDP_test', dir)

    randomly_select_files(src_directory, dest_directory)
