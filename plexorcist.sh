#!/bin/bash

GREEN=$(tput setaf 2)
RESET=$(tput sgr0)
VERSION=$(curl -s https://api.github.com/repos/stefanbc/plexorcist/releases/latest | grep -o '"tag_name": "[^"]*"' | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")

if [[ $1 == "--check" ]]; then
  INSTALLED_VERSION=$(grep -oE "[0-9]+\.[0-9]+\.[0-9]+" plexorcist/plexorcist.py)
  if [[ $INSTALLED_VERSION == $VERSION ]]; then
    echo "${GREEN}Step 1: Plexorcist is up to date.${RESET}"
  else
    echo "${GREEN}Step 1: A new version of Plexorcist is available. Current version: $INSTALLED_VERSION. Latest version: $VERSION.${RESET}"
  fi
  exit 0
fi

echo "${GREEN}Step 1: Downloading Plexorcist v${VERSION}...${RESET}"
wget -q https://github.com/stefanbc/plexorcist/archive/refs/tags/v${VERSION}.zip -O "plexorcist-${VERSION}.zip"

echo "${GREEN}Step 2: Unzipping plexorcist-${VERSION}.zip...${RESET}"
unzip -qq ./"plexorcist-${VERSION}.zip"

echo "${GREEN}Step 3: Removing plexorcist-${VERSION}.zip...${RESET}"
rm ./"plexorcist-${VERSION}.zip"

if [[ $1 == "--update" ]]; then
  echo "${GREEN}Step 4: Updating plexorcist files...${RESET}"
  cp -rf ./plexorcist-${VERSION}/* ./plexorcist/
else
  echo "${GREEN}Step 4: Renaming plexorcist-${VERSION} to plexorcist...${RESET}"
  mv -f ./"plexorcist-${VERSION}" ./plexorcist
fi

echo "${GREEN}Step 5: Installing dependencies using pip...${RESET}"
cd plexorcist
pip install -qq -r requirements.txt

echo "${GREEN}Step 6: Making plexorcist.py executable...${RESET}"
chmod +x plexorcist.py

echo "${GREEN}Step 7: Installation complete!${RESET}"
