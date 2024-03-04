#!/usr/bin/env sh

cd $HOME
# Clone the repository and install the script
echo "Cloning the repository and installing the script to ~/.local/bin/auto-dark-mode"
git clone https://github.com/braun-steven/auto-dark-mode
cd auto-dark-mode
mkdir -p ~/.local/bin/
cp auto_dark_mode.py ~/.local/bin/auto-dark-mode
chmod +x ~/.local/bin/auto-dark-mode

# Check if .local/bin is in the PATH. If not, suggest the user the command to add it to the PATH
if ! [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
  echo "The directory ~/.local/bin is not in the PATH. You can add it by running the following command:"
  echo "echo 'export PATH=\$PATH:\$HOME/.local/bin' >> ~/.bashrc"
fi

# Install the configuration file
echo "Installing the configuration file to ~/.config/auto-dark-mode/config.toml"
mkdir -p ~/.config/auto-dark-mode/

# Check if the configuration file already exists. If it does, ask the user if they want to overwrite it
if [ -f ~/.config/auto-dark-mode/config.toml ]; then
  echo "The file ~/.config/auto-dark-mode/config.toml already exists. Do you want to overwrite it? (y/n)"
  read -r answer
  if [ "$answer" = "y" ]; then
    cp config.toml ~/.config/auto-dark-mode/config.toml
  fi
fi


# Install the systemd service and timer
echo "Installing systemd service and timer"
mkdir -p ~/.config/systemd/user/
cp auto-dark-mode.service ~/.config/systemd/user/auto-dark-mode.service
cp auto-dark-mode.timer ~/.config/systemd/user/auto-dark-mode.timer
