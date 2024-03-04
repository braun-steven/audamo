# Auto Dark Mode

## Installation

### Arch Linux (AUR)

(TODO: Add to AUR)

```sh
paru -s auto-dark-mode
```

### Install Script

Install conveniently with the install script.

``` sh
curl https://github.com/braun-steven/auto-dark-mode/install.sh | bash
```

## Configuration

``` toml
# Specify location by latitude and longitude
latitude = ""
longitude = ""

# Time
sunrise = "08:00"
sunset = "20:00"

# Theme mode:
#  - "location": sets the theme based on sunrise/sunset at given location
#  - "time": sets the theme
mode = "location"


# GTK Themes
gtk-theme-light = "Adwaita"
gtk-theme-dark = "Adwaita-dark"


# External script that also gets executed
# This script may contain user specified `sed` instructions to e.g. replace the vim theme like "sed -i s/colorscheme dark/colorscheme light/g" or similar
external-script = ""
```
