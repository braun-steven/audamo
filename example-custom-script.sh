#!/usr/bin/env sh

# This is an example custom script that can be set as `custom-script-path` in the config file.
# The script gets executed with a single argument, which is either `light` or `dark` depending on the theme figured out by audamo.
# The script can be used to change the wallpaper, lock screen, etc. based on the theme.

THEME="$1"
case $THEME in
    light)
        swaymsg "output * bg ~/wallpaper-light.png fill"
        ;;
    dark)
        swaymsg "output * bg ~/wallpaper-dark.png fill"
        ;;
    *)
        echo "Invalid argument. Please use 'light' or 'dark'."
        exit 1
        ;;
esac
