#!/bin/bash

version=1.3.1

echo "Step 1: Downloading Plexorcist v${version}..."
wget https://github.com/stefanbc/Plexorcist/archive/refs/tags/v${version}.zip -O "Plexorcist-${version}.zip"

echo "Step 2: Unzipping Plexorcist-${version}.zip..."
unzip ./"Plexorcist-${version}.zip"

echo "Step 3: Removing Plexorcist-${version}.zip..."
rm ./"Plexorcist-${version}.zip"

echo "Step 4: Renaming Plexorcist-${version} to Plexorcist..."
mv ./"Plexorcist-${version}" ./Plexorcist

echo "Step 5: Installing dependencies using pip..."
cd Plexorcist
pip install -r requirements.txt

echo "Step 6: Making plexorcist.py executable..."
chmod +x plexorcist.py

echo "Step 7: Installation complete!"
