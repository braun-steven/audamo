#!/usr/bin/env python3
"""
Enhanced script to automatically change the GNOME theme between light and dark mode
based on the sunrise and sunset times. Now includes improved error handling, logging,
and allows for manual location specification.
"""

import argparse
from dataclasses import dataclass
import logging
import requests
import subprocess
from datetime import datetime
import pytz
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
import os
import tomllib
from typing import Optional
import enum
from time import sleep

logger = logging.getLogger(__name__)


# Theme enum
class Theme(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"


class Mode(str, enum.Enum):
    TIME = "time"
    LOCATION = "location"


def location_to_timezone(latitude: float, longitude: float) -> str:
    """
    Get the timezone for a given location using the timezonefinder library.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.

    Returns:
        str: Timezone string for the given location.
    """
    tf = TimezoneFinder()

    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    return timezone_str


def get_current_location_info() -> tuple[float, float, str]:
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
        return float(loc[0]), float(loc[1]), data["timezone"]
    except requests.RequestException as e:
        logging.error("Failed to fetch current location: %s", e)
        raise SystemExit("Could not determine current location. Please specify location manually.")


def get_sunrise_sunset(latitude: float, longitude: float, timezone_str: str) -> tuple[datetime, datetime]:
    """
    Get the sunrise and sunset times for a given location.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        timezone_str: Timezone string for the location.

    Returns:
        tuple: Datetime objects for the sunrise and sunset times.

    Raises:
        Exception: If an error occurs while calculating the sunrise and sunset times.
    """
    try:
        timezone = pytz.timezone(timezone_str)
        city = LocationInfo(latitude=latitude, longitude=longitude, timezone=timezone_str)
        s = sun(city.observer, date=datetime.now(timezone), tzinfo=timezone)
        return s["sunrise"], s["sunset"]
    except Exception as e:
        logging.error("Error calculating sunrise/sunset: %s", e)
        raise


def run(cmd):
    """
    Run a command in the shell.

    Args:
        cmd: Command to run as a string.

    Raises:
        subprocess.CalledProcessError: If the command fails.
    """
    try:
        subprocess.run(cmd.split(), check=True)
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", e)
        raise


def set_theme(theme: Theme, config: dict):
    """
    Set the theme based on the mode.

    Args:
        theme: Theme mode: light or dark.
        config: Configuration settings.

    Raises:
        Exception: If an error occurs while setting the theme.
    """

    logger.info("Setting theme to %s mode", theme)
    try:
        dark_theme = config["gtk-theme-dark"]
        light_theme = config["gtk-theme-light"]
        if theme == Theme.DARK:
            run(f"gsettings set org.gnome.desktop.interface gtk-theme '{dark_theme}'")
            run(f"gsettings set org.gnome.desktop.wm.preferences theme '{dark_theme}'")
            run("gsettings set org.gnome.desktop.interface color-scheme prefer-dark")
        elif theme == Theme.LIGHT:
            run(f"gsettings set org.gnome.desktop.interface gtk-theme '{light_theme}'")
            run(f"gsettings set org.gnome.desktop.wm.preferences theme '{light_theme}'")
            run("gsettings set org.gnome.desktop.interface color-scheme prefer-light")
        else:
            raise ValueError(f"Invalid theme: {theme}")

        # Run custom script if specified
        if config["custom-script-path"] is not None and config["custom-script-path"] != "":
            run_custom_script(config["custom-script-path"], theme)
    except Exception as e:
        logging.error("Failed to set theme: %s", e)
        raise


def set_theme_from_time(args: argparse.Namespace, config: dict):
    # Check if args contain sunrise and sunset times
    if args.time is not None:
        sunrise, sunset = args.time
    else:
        # Obtain time from config
        sunrise, sunset = config["sunrise"], config["sunset"]
        sunrise = datetime.strptime(sunrise, "%H:%M")
        sunset = datetime.strptime(sunset, "%H:%M")

    sunrise = sunrise.time()
    sunset = sunset.time()
    now = datetime.now().time()
    if sunrise <= now <= sunset:
        logger.info("It's daytime (sunrise to sunset)")
        set_theme(theme=Theme.LIGHT, config=config)
    else:
        logger.info("It's nighttime (sunset to sunrise)")
        set_theme(theme=Theme.DARK, config=config)


def set_theme_from_location(args: argparse.Namespace, config: dict):
    if args.location:
        # If location was explicitly specified in cmd-line arguments
        latitude, longitude = float(args.location[0]), float(args.location[1])
        timezone_str = location_to_timezone(latitude, longitude)
    elif config["latitude"] != "" and config["longitude"] != "":
        # Else, if location was specified in the config file
        latitude, longitude = float(config["latitude"]), float(config["longitude"])
        timezone_str = location_to_timezone(latitude, longitude)
    else:
        # Else, fetch the current location
        logger.info("Fetching current location...")
        latitude, longitude, timezone_str = get_current_location_info()

    # Get timezone, sunrise, sunset, and current time
    timezone = pytz.timezone(timezone_str)
    sunrise, sunset = get_sunrise_sunset(latitude, longitude, timezone_str)
    now = datetime.now(timezone)

    # Print some info
    logger.info("Location: latitude=%s, longitude=%s", latitude, longitude)
    logger.info("Timezone: %s", timezone_str)
    logger.info("Sunrise:      %s", sunrise.strftime("%H:%M:%S %Z"))
    logger.info("Sunset:       %s", sunset.strftime("%H:%M:%S %Z"))
    logger.info("Current time: %s", now.strftime("%H:%M:%S %Z"))

    current_time = now.time()
    sunrise_time = sunrise.time()
    sunset_time = sunset.time()

    if sunrise_time <= current_time <= sunset_time:
        logger.info("It's daytime (sunrise to sunset)")
        set_theme(theme=Theme.LIGHT, config=config)
    else:
        logger.info("It's nighttime (sunset to sunrise)")
        set_theme(theme=Theme.DARK, config=config)


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
            logging.FileHandler("/tmp/auto-dark-mode.log"),
        ],
    )


def load_config(args_config_path: Optional[str]) -> dict:
    """
    Load the configuration file.

    Args:
        args_config_path: Path to the configuration file.

    Returns:
        dict: Configuration settings.
    """
    if args_config_path is None:
        # If config path is not specified, use the default path at XDG_CONFIG_HOME or ~/.config/
        config_home = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        path = os.path.join(config_home, "auto-dark-mode", "config.toml")
    else:
        path = args_config_path

    with open(path, "rb") as f:
        return tomllib.load(f)


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


def set_theme_once(args, config):
    ##########################
    # Set the theme manually #
    ##########################
    if args.light:
        set_theme(Theme.LIGHT, config)
    elif args.dark:
        set_theme(Theme.DARK, config)
    elif args.time is not None:
        set_theme_from_time(args, config)
    elif args.location is not None:
        set_theme_from_location(args, config)
    elif config["mode"] == Mode.TIME:
        set_theme_from_time(args, config)
    elif config["mode"] == Mode.LOCATION:
        set_theme_from_location(args, config)


def run_as_daemon(args, config):
    """
    Run the script as a daemon to continuously monitor the time and set the theme.

    Args:
        args: Command line arguments.
        config: Configuration settings.
    """
    # Run as a daemon
    try:
        while True:
            set_theme_once(args, config)
            sleep(60 * 10)
    except KeyboardInterrupt:
        logger.info("Daemon mode interrupted.")
        logger.info("Exiting...")
        exit(0)


def main():
    """Main function to parse command line arguments and set the theme."""

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
        help="Set theme to light mode.",
    )
    parser.add_argument(
        "-d",
        "--dark",
        action="store_true",
        help="Set theme to dark mode.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging to console.",
    )

    parser.add_argument(
        "--location",
        nargs=2,
        metavar=("LATITUDE", "LONGITUDE"),
        type=float,
        help="Manually specify location as latitude and longitude.",
    )
    parser.add_argument(
        "--time",
        nargs=2,
        metavar=("SUNRISE", "SUNSET"),
        type=lambda x: datetime.strptime(x, "%H:%M"),
        help="Manually specify sunrise and sunset times.",
    )
    parser.add_argument(
        "--daemon", action="store_true", help="Run as a daemon to continuously monitor the time."
    )
    # Add a new argument to specify the configuration file
    parser.add_argument(
        "-c",
        "--config",
        help="Specify the configuration file to use",
        type=lambda x: (os.path.exists(x) and x) or parser.error(f"File does not exist: {x}"),
    )

    args = parser.parse_args()
    setup_logging(args.debug)

    # Parse the configuration file
    config = load_config(args.config)

    # Check that the user didn't set both light and dark mode at the same time
    if args.light and args.dark:
        logger.error("Cannot set both light and dark mode at the same time.")
        exit(1)

    if not args.daemon:
        # Set the theme manually
        set_theme_once(args, config)
    else:
        # Run as a daemon
        run_as_daemon(args, config)


if __name__ == "__main__":
    main()
