#!/bin/bash

version=1.3.4

echo "Step 1: Downloading Plexorcist v${version}..."
wget https://github.com/stefanbc/plexorcist/archive/refs/tags/v${version}.zip -O "plexorcist-${version}.zip"

echo "Step 2: Unzipping plexorcist-${version}.zip..."
unzip ./"plexorcist-${version}.zip"

echo "Step 3: Removing plexorcist-${version}.zip..."
rm ./"plexorcist-${version}.zip"

echo "Step 4: Renaming plexorcist-${version} to plexorcist..."
mv ./"plexorcist-${version}" ./plexorcist

echo "Step 5: Installing dependencies using pip..."
cd plexorcist
pip install -r requirements.txt

echo "Step 6: Making plexorcist.py executable..."
chmod +x plexorcist.py

echo "Step 7: Installation complete!"
