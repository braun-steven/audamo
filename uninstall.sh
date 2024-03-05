#!/usr/bin/env sh
# Uninstall script for 'audamo'

echo "Removing installed script and configuration files..."

# Remove script from ~/.local/bin
if [ -f ~/.local/bin/audamo ]; then
    rm ~/.local/bin/audamo
    echo "Removed script: ~/.local/bin/audamo"
fi

# Remove configuration file (with prompt)
if [ -f ~/.config/audamo/config.toml ]; then
    echo "Remove configuration file ~/.config/audamo/config.toml? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        rm ~/.config/audamo/config.toml
        echo "Removed configuration file."
    else
        echo "Keeping configuration file."
    fi
fi

# Remove systemd service and timer files
if [ -d ~/.config/systemd/user ]; then
    rm -f ~/.config/systemd/user/audamo.service
    rm -f ~/.config/systemd/user/audamo.timer
    echo "Removed systemd service and timer files."
fi

echo "Uninstall complete!"
