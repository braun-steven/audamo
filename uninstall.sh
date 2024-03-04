#!/usr/bin/env sh
# Uninstall script for 'auto-dark-mode'

echo "Removing installed script and configuration files..."

# Remove script from ~/.local/bin
if [ -f ~/.local/bin/auto-dark-mode ]; then
    rm ~/.local/bin/auto-dark-mode
    echo "Removed script: ~/.local/bin/auto-dark-mode"
fi

# Remove configuration file (with prompt)
if [ -f ~/.config/auto-dark-mode/config.toml ]; then
    echo "Remove configuration file ~/.config/auto-dark-mode/config.toml? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        rm ~/.config/auto-dark-mode/config.toml
        echo "Removed configuration file."
    else
        echo "Keeping configuration file."
    fi
fi

# Remove systemd service and timer files
if [ -d ~/.config/systemd/user ]; then
    rm -f ~/.config/systemd/user/auto-dark-mode.service
    rm -f ~/.config/systemd/user/auto-dark-mode.timer
    echo "Removed systemd service and timer files."
fi

echo "Uninstall complete!"
