import os
import shutil
from glob import glob

# Get all directories inside "./all_answers"
all_pubs = glob("./all_answers/*")

# Create the backup directory if it doesn't already exist
os.makedirs("./all_answers_backup", exist_ok=True)

# Loop through each publication directory
for pub in all_pubs:
    # Get all `.yaml_backup` files in the current publication directory
    all_journals = glob(pub + "/*.yaml_backup")
    for j in all_journals:
        # Define the destination path in the backup directory
        backup_dir = pub.replace("all_answers", "all_answers_backup")
        os.makedirs(
            backup_dir, exist_ok=True
        )  # Ensure the backup directory exists

        # Define the target path for the backup file
        target_path = os.path.join(backup_dir, os.path.basename(j))

        # Move the file to the backup directory
        shutil.move(j, target_path)

        # Print the path of the moved file
        print(f"Moved: {j} -> {target_path}")
