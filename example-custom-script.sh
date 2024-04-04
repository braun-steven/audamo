#!/usr/bin/env sh

# This is an example custom script that can be set as `custom-script-path` in the config file.
# The script gets executed with a single argument, which is either `light` or `dark` depending on the theme figured out by audamo.
# The script can be used to change the wallpaper, lock screen, etc. based on the theme.

THEME="$1"
case $THEME in
    light)
        # Sway background
        swaymsg "output * bg ~/lakesidedeer-light.png fill"

        # Alacritty
        sed -i 's/nord/github_light/g' ~/.config/alacritty/alacritty.toml

        # Vim
        sed -i 's/background=dark/background=light/g' ~/.vimrc
        ;;
    dark)
        # Sway background
        swaymsg "output * bg ~/lakesidedeer-dark.png fill"

        # Alacritty
        sed -i 's/github_light/nord/g' ~/.config/alacritty/alacritty.toml

        # Vim
        sed -i 's/background=light/background=dark/g' ~/.vimrc
        ;;
    *)
        echo "Invalid argument. Please use 'light' or 'dark'."
        exit 1
        ;;
esac
