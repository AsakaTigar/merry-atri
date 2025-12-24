import sys
import os

# Add krkr-xp3 to sys.path
sys.path.append('krkr-xp3')
try:
    from xp3reader import XP3Reader
except ImportError:
    print("Error: Could not import xp3reader. Make sure krkr-xp3 is in the directory.")
    sys.exit(1)

# Paths
xp3_path = "/mnt/x/SteamLibrary/steamapps/common/ATRI -My Dear Moments-/vol1.xp3"
output_dir = "extracted"

if not os.path.exists(xp3_path):
    print(f"Error: XP3 file not found at {xp3_path}")
    sys.exit(1)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Opening {xp3_path}...")

try:
    with open(xp3_path, 'rb') as f:
        # xp3reader uses numpy if available, handles optionality internally
        with XP3Reader(f) as reader:
            print(f"Found {len(reader.file_index.entries)} files.")
            count = 0
            for file in reader:
                path = file.info.file_path
                # Filter for voice (.opus) and script (.scn)
                if path.endswith('.opus') or path.endswith('.scn'):
                    # print(f"Extracting {path}...")
                    try:
                        # Extract handles directory creation
                        file.extract(to=output_dir)
                        count += 1
                        if count % 100 == 0:
                            print(f"Extracted {count} files...")
                    except Exception as e:
                        print(f"Failed to extract {path}: {e}")
    print(f"Extraction complete. Total extracted: {count}")
except Exception:
    import traceback
    traceback.print_exc()
