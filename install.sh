#!/usr/bin/env sh

cd $HOME
# Clone the repository and install the script
echo "Cloning the repository and installing the script to ~/.local/bin/audamo"

# Check if ~/auto-darm-mode already exists. If it does, cd into the dir and run git pull
if [ -d ~/audamo ]; then
  cd ~/audamo
  git pull
else
    git clone https://github.com/braun-steven/audamo
    cd audamo
fi

# Ensure that ~/.local/bin exists and copy the script to it
mkdir -p ~/.local/bin/
cp auto_dark_mode.py ~/.local/bin/audamo
chmod +x ~/.local/bin/audamo

# Check if .local/bin is in the PATH. If not, suggest the user the command to add it to the PATH
if ! [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
  echo "The directory ~/.local/bin is not in the PATH. You can add it by running the following command:"
  echo "echo 'export PATH=\$PATH:\$HOME/.local/bin' >> ~/.bashrc"
fi

# Install the configuration file
echo "Installing the configuration file to ~/.config/audamo/config.toml"
mkdir -p ~/.config/audamo/

# Check if the configuration file already exists. If it does, ask the user if they want to overwrite it
if [ -f ~/.config/audamo/config.toml ]; then
  echo "The file ~/.config/audamo/config.toml already exists. Do you want to overwrite it? (y/n)"
  read -r answer
  if [ "$answer" = "y" ]; then
    cp config.toml ~/.config/audamo/config.toml
  fi
else
    cp config.toml ~/.config/audamo/config.toml
fi



# Install the systemd service and timer
echo "Installing systemd service"
mkdir -p ~/.config/systemd/user/
cp audamo.service ~/.config/systemd/user/audamo.service
