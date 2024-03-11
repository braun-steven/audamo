#!/usr/bin/env python3
__author__ = "Steven Braun"
__email__ = "steven.braun.mz@gmail.com"
__version__ = "1.1.1"
__license__ = "MIT"

import argparse
import logging
import requests
import subprocess
from datetime import datetime

from astral import LocationInfo
from astral.sun import sun
import os
import tomli
from typing import Optional
import enum
from time import sleep

logger = logging.getLogger(__name__)


class Theme(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"


class Mode(str, enum.Enum):
    TIME = "time"
    LOCATION = "location"


def get_sunrise_sunset(cfg: dict) -> tuple[datetime, datetime]:
    """
    Get the sunrise and sunset times based on the mode.

    Args:
        cfg: Configuration settings.

    Returns:
        tuple: Datetime objects for the sunrise and sunset times.
    """

    if cfg["general"]["mode"] == Mode.TIME:
        # Get sunrise and sunset times from config
        logger.info("Using sunrise and sunset times from config")
        sunrise, sunset = get_sunrise_sunset_from_config(cfg)

    elif cfg["general"]["mode"] == Mode.LOCATION:
        # Get sunrise and sunset times from location
        logger.info("Using sunrise and sunset times from location")
        sunrise, sunset = get_sunrise_sunset_from_location(cfg)

    else:
        raise ValueError(f"Invalid mode: {cfg['general']['mode']}")

    # Construct sunrise and sunset for today
    now = datetime.now().astimezone()
    sunrise = now.replace(hour=sunrise.hour, minute=sunrise.minute, second=0, microsecond=0)
    sunset = now.replace(hour=sunset.hour, minute=sunset.minute, second=0, microsecond=0)
    return sunrise, sunset


def get_sunrise_sunset_from_location(cfg: dict) -> tuple[datetime, datetime]:
    """
    Get the sunrise and sunset times for a given location.

    Args:
        cfg: Configuration settings.

    Returns:
        tuple: Datetime objects for the sunrise and sunset times.

    Raises:
        Exception: If an error occurs while calculating the sunrise and sunset times.
    """

    try:
        if lat_lon_is_missing(cfg):
            # fetch the current location
            logger.info("Fetching current location...")
            latitude, longitude = get_current_location_info()
        else:
            # Else, if location was specified in the config file
            latitude, longitude = float(cfg["general"]["latitude"]), float(cfg["general"]["longitude"])

        city = LocationInfo(latitude=latitude, longitude=longitude)
        s = sun(city.observer)
        return s["sunrise"], s["sunset"]
    except Exception as e:
        logging.error("Error calculating sunrise/sunset: %s", e)
        raise


def get_sunrise_sunset_from_config(cfg: dict) -> tuple[datetime, datetime]:
    """
    Get the sunrise and sunset times from the configuration file.

    Args:
        cfg: Configuration settings.

    Returns:
        tuple: Datetime objects for the sunrise and sunset times.
    """

    # Get sunrise and sunset times from config
    try:
        sunrise = datetime.strptime(cfg["general"]["sunrise"], "%H:%M")
        sunset = datetime.strptime(cfg["general"]["sunset"], "%H:%M")
        return sunrise, sunset
    except ValueError as e:
        logging.error("Error parsing sunrise/sunset from config: %s", e)
        raise


def get_current_location_info() -> tuple[float, float]:
    """
    Get the current location and timezone using the ipinfo.io API.

    Returns:
        tuple: Latitude, longitude, and timezone for the current location.

    Raises:
        SystemExit: If the location could not be determined.
    """
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()  # Raises an HTTPError if the response was an error
        data = response.json()
        loc = data["loc"].split(",")
        return float(loc[0]), float(loc[1])
    except requests.RequestException as e:
        logging.error("Failed to fetch current location: %s", e)
        raise SystemExit("Could not determine current location. Please specify location manually.")


def lat_lon_is_missing(cfg: dict) -> bool:
    """
    Check if latitude and longitude are missing in the configuration file.

    Args:
        cfg: Configuration settings.

    Returns:
        bool: True if latitude and longitude are missing, False otherwise.
    """
    return cfg["general"]["latitude"] == "" or cfg["general"]["longitude"] == ""


def run(cmd):
    """
    Run a command in the shell.

    Args:
        cmd: Command to run as a string.

    Raises:
        subprocess.CalledProcessError: If the command fails.
    """
    try:
        logger.info("Running command: %s", cmd)
        subprocess.run(cmd.split(), check=True)
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", e)
        raise


def set_theme(cfg: dict, theme: Theme):
    """
    Set the theme based on the mode.

    Args:
        theme: Theme mode: light or dark.

    Raises:
        Exception: If an error occurs while setting the theme.
    """

    logger.info("Setting theme to %s mode", theme)
    available_themes = find_available_themes()
    try:
        d = cfg[theme.value]

        # THEME
        if d["theme"] != "":  # Only set the theme if it's not empty
            if d["theme"] not in available_themes["theme"]:  # Check if theme exists
                logger.warning(f"Theme not found: {d['theme']}. Must be one of: {available_themes['theme']}")

            run(f"gsettings set org.gnome.desktop.interface gtk-theme '{d['theme']}'")
            run(f"gsettings set org.gnome.desktop.wm.preferences theme '{d['theme']}'")
            run(f"gsettings set org.gnome.desktop.interface color-scheme prefer-{theme.value}")

        # ICON
        if d["icon"] != "":  # Only set the icon if it's not empty
            if d["icon"] not in available_themes["icon"]:  # Check if icon exists
                logger.warning(f"Icon not found: {d['icon']}. Must be one of: {available_themes['icon']}")

            run(f"gsettings set org.gnome.desktop.interface icon-theme '{d['icon']}'")

        # CURSOR
        if d["cursor"] != "":  # Only set the cursor if it's not empty
            if d["cursor"] not in available_themes["cursor"]:  # Check if cursor exists
                logger.warning(
                    f"Cursor not found: {d['cursor']}. Must be one of: {available_themes['cursor']}"
                )
            run(f"gsettings set org.gnome.desktop.interface cursor-theme '{d['cursor']}'")

        # Run custom script if specified
        if cfg["general"]["custom-script-path"] is not None and cfg["general"]["custom-script-path"] != "":
            run_custom_script(cfg["general"]["custom-script-path"], theme)
    except Exception as e:
        logging.error("Failed to set theme: %s", e)
        raise e

    # Write current theme to a temporary file
    with open("/tmp/audamo_current-theme", "w") as f:
        f.write(theme.value)


def set_theme_once(cfg: dict):
    """
    Set the theme based on the sunrise and sunset times.

    Based on the selected mode, these can be inferred from the configuration file or calculated based on the location.

    Args:
        cfg: Configuration settings.

    Raises:
        Exception: If an error occurs while setting the theme.
    """
    sunrise, sunset = get_sunrise_sunset(cfg)
    now = datetime.now()

    logger.info("Sunrise:      %s", sunrise.strftime("%H:%M:%S %Z"))
    logger.info("Sunset:       %s", sunset.strftime("%H:%M:%S %Z"))
    logger.info("Current time: %s", now.strftime("%H:%M:%S %Z"))

    if sunrise.time() <= now.time() <= sunset.time():
        logger.info("It's daytime (sunrise to sunset)")
        set_theme(cfg=cfg, theme=Theme.LIGHT)
    else:
        logger.info("It's nighttime (sunset to sunrise)")
        set_theme(cfg=cfg, theme=Theme.DARK)


def setup_logging(debug: bool):
    """
    Set up basic logging. Enables stream and file handlers.

    Args:
        debug: Enable debug logging to console.
    """
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("/tmp/audamo.log"),
        ],
    )


def get_config_path(args_config_path: Optional[str]) -> str:
    if args_config_path is None:
        # If config path is not specified, use the default path at XDG_cfg_HOME or ~/.config/
        config_home = os.getenv("XDG_cfg_HOME", os.path.expanduser("~/.config"))
        path = os.path.join(config_home, "audamo", "config.toml")

        if not os.path.exists(path):
            logger.warning(
                "No config file found at %s, using system config at /usr/share/audamo/config.toml", path
            )

            # Set new default path
            path = "/usr/share/audamo/config.toml"
            if not os.path.exists(path):
                logger.error("No system config file found at %s, exiting now.", path)
                exit(0)
    else:
        path = args_config_path

    return path


def load_config(args_config_path: Optional[str]) -> dict:
    """
    Load the configuration file.

    Args:
        args_config_path: Path to the configuration file.

    Returns:
        dict: Configuration settings.
    """

    path = get_config_path(args_config_path)
    with open(path, "rb") as f:
        return tomli.load(f)


def run_custom_script(script_path: str, theme: Theme):
    """
    Run a custom script.

    Args:
        script_path: Path to the custom script to run.
        theme: Theme mode: light or dark.

    """
    # Check if script path exists and is executable
    script_path = os.path.expanduser(script_path)

    logger.info("Running custom script: %s", script_path)
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    if not os.access(script_path, os.X_OK):
        raise PermissionError(f"Script is not executable: {script_path}")

    # Run the script
    try:
        subprocess.run([script_path, theme], check=True)
    except subprocess.CalledProcessError as e:
        logging.error("Script failed: %s", e)
        raise e


def run_as_daemon():
    """
    Run the script as a daemon to continuously monitor the time and set the theme.

    Args:
        args: Command line arguments.
    """
    # Run as a daemon
    try:
        while True:
            # Load configuration file again in case it was changed during runtime
            cfg = load_config(None)
            set_theme_once(cfg)

            # Sleep for 10 minutes
            sleep_seconds += 60 * 10

            # Sleep until next sunrise/sunset
            sleep(sleep_seconds)
    except KeyboardInterrupt:
        logger.info("Daemon mode interrupted.")
        logger.info("Exiting...")
        exit(0)


def find_available_themes():
    """Returns a dictionary containing lists of available themes, cursors, and icons.

    Searches directories specified in the XDG_DATA_DIRS environment variable
    as well as $HOME/.themes and $HOME/.icons.
    """

    result = {"theme": [], "cursor": [], "icon": []}
    xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
    theme_dirs = [os.path.join(d, "themes") for d in xdg_data_dirs] + [
        os.path.join(os.path.expanduser("~"), ".themes")
    ]
    icon_dirs = [os.path.join(d, "icons") for d in xdg_data_dirs] + [
        os.path.join(os.path.expanduser("~"), ".icons")
    ]
    cursor_dirs = icon_dirs

    # Themes
    for themes_dir in theme_dirs:
        if os.path.exists(themes_dir):
            for theme_candidate in os.listdir(themes_dir):
                full_theme_path = os.path.join(themes_dir, theme_candidate)
                if os.path.isdir(full_theme_path):
                    result["theme"].append(theme_candidate)

    # Icons
    for icon_dir in icon_dirs:
        if os.path.exists(icon_dir):
            for icon_candidate in os.listdir(icon_dir):
                full_icon_path = os.path.join(icon_dir, icon_candidate)
                if os.path.isdir(full_icon_path):
                    result["icon"].append(icon_candidate)

    # Cursors
    for cursor_dir in cursor_dirs:
        if os.path.exists(cursor_dir):
            for cursor_candidate in os.listdir(cursor_dir):
                full_cursor_path = os.path.join(cursor_dir, cursor_candidate)
                if os.path.isdir(full_cursor_path):
                    result["cursor"].append(cursor_candidate)

    # Make sure there are no duplicates and sort lists
    for key in result:
        result[key] = sorted(list(set(result[key])))

    return result


def list_themes():
    available_themes = find_available_themes()
    print("Available themes:")
    print("Themes:\n- " + "\n- ".join(available_themes["theme"]))
    print("Cursors:\n- " + "\n- ".join(available_themes["cursor"]))
    print("Icons:\n- " + "\n- ".join(available_themes["icon"]))


def main(args):
    # Print the configuration file and exit
    if args.print_config:
        with open(get_config_path(args.config), "r") as f:
            print(f.read())
        exit(0)

    # List available themes, cursors, and icons
    if args.list_themes:
        list_themes()
        exit(0)

    # Check that the user didn't set both light and dark mode at the same time
    if args.light and args.dark:
        logger.error("Cannot set both light and dark mode at the same time.")
        exit(1)

    # Parse the configuration file
    cfg = load_config(args.config)

    # Check if the user set light or dark mode manually
    if args.light:
        set_theme(cfg, Theme.LIGHT)
        exit(0)
    elif args.dark:
        set_theme(cfg, Theme.DARK)
        exit(0)

    if args.daemon:
        # Run as a daemon
        run_as_daemon()
    else:
        # Set the theme manually
        set_theme_once(cfg)


if __name__ == "__main__":
    ###############################
    # Parse commandline arguments #
    ###############################
    parser = argparse.ArgumentParser(
        description="Automatically set the system theme based on time or local sunrise and sunset.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-l",
        "--light",
        action="store_true",
        help="Force theme to light mode.",
    )
    parser.add_argument(
        "-d",
        "--dark",
        action="store_true",
        help="Force theme to dark mode.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging to console.",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List available themes, cursors, and icons.",
    )

    parser.add_argument(
        "--daemon", action="store_true", help="Run as a daemon to continuously monitor the time."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"audamo {__version__}",
    )
    # Add a new argument to specify the configuration file
    parser.add_argument(
        "-c",
        "--config",
        help="Specify the configuration file to use",
        type=lambda x: (os.path.exists(x) and x) or parser.error(f"File does not exist: {x}"),
    )

    parser.add_argument(
        "--print-config",
        action="store_true",
        help="Print the configuration file and exit.",
    )

    args = parser.parse_args()
    setup_logging(args.debug)

    # Run main function
    main(args)
