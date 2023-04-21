#!/bin/bash

# Clone Plexorcist
git clone https://github.com/stefanbc/Plexorcist.git

# Open Plexorcist
cd Plexorcist

# Install the dependencies
pip install -r requirements.txt

# Give permissions to Plexorcist
chmod +x plexorcist.py
