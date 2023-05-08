#!/bin/bash

echo -e "\e[32mStep 1:\e[0m Fetching the latest release information from GitHub..."
version=$(curl -s https://api.github.com/repos/stefanbc/plexorcist/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
echo "Latest version: $version"

echo -e "\e[32mStep 2:\e[0m Downloading Plexorcist v${version}..."
wget -q https://github.com/stefanbc/plexorcist/archive/refs/tags/v${version}.zip -O "plexorcist-${version}.zip"

echo -e "\e[32mStep 3:\e[0m Unzipping plexorcist-${version}.zip..."
unzip -q ./"plexorcist-${version}.zip"

echo -e "\e[32mStep 4:\e[0m Removing plexorcist-${version}.zip..."
rm -f ./"plexorcist-${version}.zip"

update=$1

if [ "$update" = "update" ]; then
    echo -e "\e[32mStep 5:\e[0m Updating plexorcist..."
    cp -rf "./plexorcist-${version}/*" ./plexorcist/
else
    echo -e "\e[32mStep 5:\e[0m Renaming plexorcist-${version} to plexorcist..."
    mv -f ./"plexorcist-${version}" ./plexorcist
fi

echo -e "\e[32mStep 6:\e[0m Installing dependencies using pip..."
cd ./plexorcist
pip install -q -r requirements.txt

echo -e "\e[32mStep 7:\e[0m Making plexorcist.py executable..."
chmod +x ./plexorcist.py

echo -e "\e[32mStep 8:\e[0m Installation complete!"

