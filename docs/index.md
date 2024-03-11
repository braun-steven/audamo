---
layout: default
---

![Python Version](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![AUR](https://img.shields.io/aur/version/audamo)

# Audamo
 <img align="right" src='https://raw.githubusercontent.com/braun-steven/audamo/main/docs/res/logo.png' width='20%'>

Audamo is a project designed to smoothly provide what fully featured desktop environments such as Gnome and KDE provide: An automated transition of themes between light and dark mode depending on time or location. This is particularly helpful for non-desktop environments such as i3wm, sway, hyprland, awesomewm, bspwm, dwm, and many more. Audamo can be configured to switch themes based on sunrise/sunset times at a given or inferred location or simply by a specified schedule. Additionally, Audamo allows for the execution of custom scripts during theme changes, enabling users to hook up additional scripts into the theme toggle process.

Until now, Audamo can set the following theme elements (`config.toml` values in brackets, see also [Configuration](#configuration)):

- GTK theme (`theme`)
- Icon theme (`icon`)
- Cursor theme (`cursor`)
- GTK color-scheme preference

A user specified script (`custom-script-path`) can be run with every theme change, allowing for additional customization, see also [Custom Script](#custom-script).

</br>

## Installation

### Install Script

Install conveniently with the [install script](https://raw.githubusercontent.com/braun-steven/audamo/main/install.sh).

``` bash
bash <(curl -s -L https://raw.githubusercontent.com/braun-steven/audamo/main/install.sh)
```

#### Dependencies

Audamo requires the following python packages to be installed (see [requirements.txt](https://raw.githubusercontent.com/braun-steven/audamo/main/install.sh) for more specific versions):

- `astral`
- `requests`
- `tomli`

### Arch Linux (AUR)

Audamo is available in the AUR as `audamo`:

```bash
paru -S audamo
```

You can now copy the default system-wide configuration into your user config:

``` bash
cp /usr/share/audamo/config.toml $XDG_CONFIG_HOME/audamo/config.toml
```

## Usage

Audamo is intended to be run as a background process which checks for location or time and based on this applies a dark or light settings defined in `config.toml`. 

### Systemd

We provide systemd user units to run `audamo --daemon` as a serviced service as well:

```bash
systemctl --user enable --now audamo.service
```

### Daemon Mode

If systemd is not available or not desired, `audamo` can also be run in daemon mode:

``` bash
audamo --daemon
```

### Manual

Instead of using Audamo as a service/daemon, you can also run it manually with a single invocation. Based on the `config.toml` settings, this will update the theme to light/dark mode:

``` bash
$ audamo --help
usage: audamo [-h] [-l] [-d] [--debug] [--list-themes] [--daemon] [-v] [-c CONFIG] [--print-config]

Automatically set the system theme based on time or local sunrise and sunset.

options:
  -h, --help            show this help message and exit
  -l, --light           Force theme to light mode. (default: False)
  -d, --dark            Force theme to dark mode. (default: False)
  --debug               Enable debug logging to console. (default: False)
  --list-themes         List available themes, cursors, and icons. (default: False)
  --daemon              Run as a daemon to continuously monitor the time. (default: False)
  -v, --version         show program's version number and exit
  -c CONFIG, --config CONFIG
                        Specify the configuration file to use (default: None)
  --print-config        Print the configuration file and exit. (default: False)
```

## Configuration

Audamo can be configured by editing the `config.toml` file. The user configuration should be placed at `$XDG_CONFIG_HOME/audamo/config.toml`.

``` toml
# Specify location by latitude and longitude
[general]
latitude = ""
longitude = ""

# Time in the format "%H:%M"
sunrise = "08:00"
sunset = "20:00"

# Theme mode:
#  - "location": sets the theme based on sunrise/sunset at given location
#  - "time": sets the theme
mode = "location"

# Custom script that also gets executed with a single argument which is either "light" or "dark"
# This script may contain user specified `sed` instructions to e.g. replace the vim theme like "sed -i s/colorscheme dark/colorscheme light/g ~/.vimrc" or similar
# Make sure that the script has a proper shebang, e.g. "#!/bin/sh" for shell scripts
custom-script-path = ""

# Light theme elements
# Set values to "" if they should not be changed
[light]
theme = "Adwaita"
icon = "Adwaita"
cursor = "Adwaita"

# Dark theme elements
# Set values to "" if they should not be changed
[dark]
theme = "Adwaita-dark"
icon = "Adwaita"
cursor = "Adwaita"
```

## Custom Script

A custom script can get executed with every time `audamo` is run. The script path can be configured in `config.toml` with the  `custom-script-path` variable. The script is run with a single argument which is either "light" or "dark". This script may contain user specified `sed` instructions to e.g. replace the vim theme like `sed -i s/colorscheme dark/colorscheme light/g ~/.vimrc` or similar. Make sure that the script has a proper shebang, e.g. `#!/bin/sh` for shell scripts.

An example script can be found in [`example-custom-script.sh`](example-custom-script.sh):

```bash
#!/usr/bin/env sh

# This is an example custom script that can be set as `custom-script-path` in the config file.

if [ "$1" = "light" ]; then
    echo "Custom script called in light mode!"
elif [ "$1" = "dark" ]; then
    echo "Custom script called in dark mode!"
fi
```


## Uninstall

If Audamo was installed via the [install script](https://raw.githubusercontent.com/braun-steven/audamo/main/install.sh), it can likewise be uninstalled with the [uninstall script](https://raw.githubusercontent.com/braun-steven/audamo/main/uninstall.sh):

``` bash
bash <(curl -s -L https://raw.githubusercontent.com/braun-steven/audamo/main/uninstall.sh)
```

## Changelog

### Version 1.1.1

- Remove sleep until next sunrise/sunset as this was not compatible with suspending systems

### Version 1.1.0

- Add print config flag
- Implement sleep until next sunrise/sunset
- Fix theme detection when theme do not have an `index.theme` file
- Rewrite core logic
- Get rid of timezonefinder dependency
- Remove systemd timer and make the service start the daemon
