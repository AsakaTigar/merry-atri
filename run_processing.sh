#!/bin/bash
set -e

echo "Step 1: Decompiling SCN files..."
# Using powershell from WSL to run the Windows compilation script
powershell.exe -ExecutionPolicy Bypass -File decompile_scns.ps1

echo "Step 2: Parsing Scripts..."
# Ensure atri_extract_toolbox is in python path or referenced correctly
python3 atri_extract_toolbox/parse_script.py -i extracted -o parsed -af mp3 -s

echo "Step 3: Converting Audio (using 16 threads, MP3)..."
python3 atri_extract_toolbox/batch_convert.py -i extracted -o converted -f mp3 -t 16

echo "Processing Complete!"
echo "Data is in 'parsed' (text) and 'converted' (audio) folders."
