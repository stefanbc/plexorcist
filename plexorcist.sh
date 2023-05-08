#!/bin/bash

GREEN=$(tput setaf 2)
RESET=$(tput sgr0)
VERSION=$(curl -s https://api.github.com/repos/stefanbc/plexorcist/releases/latest | grep -o '"tag_name": "[^"]*"' | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")

if [[ $1 == "--check" ]]; then
  INSTALLED_VERSION=$(grep -oE "[0-9]+\.[0-9]+\.[0-9]+" plexorcist/plexorcist.py)
  if [[ $INSTALLED_VERSION == $VERSION ]]; then
    echo "${GREEN}Step 1:${RESET} Plexorcist is up to date!"
  else
    echo "${GREEN}Step 1:${RESET} A new version of Plexorcist is available! Current version: ${GREEN}$INSTALLED_VERSION${RESET}. Latest version: ${GREEN}$VERSION${RESET}."
  fi
  exit 0
fi

echo "${GREEN}Step 1:${RESET} Downloading Plexorcist ${GREEN}v${VERSION}${RESET} ..."
wget -q https://github.com/stefanbc/plexorcist/archive/refs/tags/v${VERSION}.zip -O "plexorcist-${VERSION}.zip"

echo "${GREEN}Step 2:${RESET} Unzipping ${GREEN}plexorcist-${VERSION}.zip${RESET} ..."
unzip -qq ./"plexorcist-${VERSION}.zip"

echo "${GREEN}Step 3:${RESET} Removing ${GREEN}plexorcist-${VERSION}.zip${RESET} ..."
rm ./"plexorcist-${VERSION}.zip"

if [[ $1 == "--update" ]]; then
  echo "${GREEN}Step 4:${RESET} Updating plexorcist files ..."
  cp -rf ./plexorcist-${VERSION}/* ./plexorcist/
else
  echo "${GREEN}Step 4:${RESET} Renaming ${GREEN}plexorcist-${VERSION}${RESET} to ${GREEN}plexorcist${RESET} ..."
  mv -f ./"plexorcist-${VERSION}" ./plexorcist
fi

echo "${GREEN}Step 5:${RESET} Installing dependencies using pip ..."
cd plexorcist
pip install -qq -r requirements.txt

echo "${GREEN}Step 6:${RESET} Making plexorcist.py executable ..."
chmod +x plexorcist.py

echo "${GREEN}Step 7:${RESET} Installation complete!"
