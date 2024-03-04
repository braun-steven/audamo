# Auto Dark Mode

## Installation

### Install Script

Install conveniently with the install script.

``` sh
curl https://github.com/braun-steven/auto-dark-mode/install.sh | bash
```

### Arch Linux (AUR)

(TODO: Add to AUR)

```sh
paru -s auto-dark-mode
```


## Configuration

``` toml
# Specify location by latitude and longitude
latitude = ""
longitude = ""

# Time in the format "%H:%M"
sunrise = "08:00"
sunset = "20:00"

# Theme mode:
#  - "location": sets the theme based on sunrise/sunset at given location
#  - "time": sets the theme
mode = "location"


# GTK Themes for light and dark mode
gtk-theme-light = "Adwaita"
gtk-theme-dark = "Adwaita-dark"


# Custom script that also gets executed with a single argument which is either "light" or "dark"
# This script may contain user specified `sed` instructions to e.g. replace the vim theme like "sed -i s/colorscheme dark/colorscheme light/g ~/.vimrc" or similar
# Make sure that the script has a proper shebang, e.g. "#!/bin/sh" for shell scripts
custom-script-path = ""
```

## Custom Script

A custom script can get executed with every time `auto-dark-mode` is run. The script path can be configured in `config.toml` with the  `custom-script-path` variable. The script is run with a single argument which is either "light" or "dark". This script may contain user specified `sed` instructions to e.g. replace the vim theme like `sed -i s/colorscheme dark/colorscheme light/g ~/.vimrc` or similar. Make sure that the script has a proper shebang, e.g. `#!/bin/sh` for shell scripts.

An example script can be found in [`example-custom-script.sh`](example-custom-script.sh):

```
#!/usr/bin/env sh

# This is an example custom script that can be set as `custom-script-path` in the config file.

if [ "$1" = "light" ]; then
    echo "Custom script called in light mode!"
elif [ "$1" = "dark" ]; then
    echo "Custom script called in dark mode!"
fi
```
