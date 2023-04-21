#!/bin/bash

version=1.3.0

# Get latest version
wget https://github.com/stefanbc/Plexorcist/archive/refs/tags/v${version}.zip -O "Plexorcist-${version}.zip"

# Unzip the file
unzip ./"Plexorcist-v${version}.zip"

# Removes zip file
rm ./"Plexorcist-v${version}.zip"

# Move the folder
mv ./"Plexorcist-v${version}" ./Plexorcist

# Open Plexorcist
cd Plexorcist

# Install the dependencies
pip install -r requirements.txt

# Give permissions to Plexorcist
chmod +x plexorcist.py
