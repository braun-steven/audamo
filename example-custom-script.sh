#!/usr/bin/env sh

# This is an example custom script that can be set as `custom-script-path` in the config file.
# The script gets executed with a single argument, which is either `light` or `dark` depending on the theme figured out by auto-dark-mode.
# The script can be used to change the wallpaper, lock screen, etc. based on the theme.

if [ "$1" = "light" ]; then
    echo "Custom script called in light mode!"
elif [ "$1" = "dark" ]; then
    echo "Custom script called in dark mode!"
fi
