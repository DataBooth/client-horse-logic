# To execute this script, you need to have python installed on your computer.
# Then, you can either run it from the command line by typing:
#
# python show_python_info.py
#
# or double-click on the file if your operating system supports it.
# The script will create a text file named python_info.txt in the same folder as
# the script and also print the same information to the console.

import sys
import platform

try:
    # Python 3.8 and newer
    from importlib.metadata import distributions
except ImportError:
    # Python 3.7 and older
    try:
        from importlib_metadata import distributions
    except ImportError:
        print("The required module 'importlib_metadata' is not installed.")
        print("To install it, run: pip install importlib_metadata")
        raise SystemExit


def get_installed_packages():
    # Get the list of installed distributions
    installed_packages = [f"{dist.metadata['Name']}=={dist.version}" for dist in distributions()]
    # Sort the list of installed packages alphabetically
    installed_packages.sort()
    # Join the list into a single string with each package on a new line, without a comma
    installed_packages_str = "\n".join(installed_packages)
    # Return the formatted string of installed packages
    return installed_packages_str


# Define a function to get the python version, platform information and installed packages
def get_system_info():
    # Get the python version
    python_version = sys.version
    # Get the platform information
    platform_info = platform.platform()
    # Get the installed packages
    installed_packages = get_installed_packages()
    # Return a tuple of the results
    return (python_version, platform_info, installed_packages)


# Define a function to write the system info to a text file
def write_system_info_to_file(filename):
    # Open the file in write mode
    with open(filename, "w") as f:
        # Get the system info
        python_version, platform_info, installed_packages_str = get_system_info()
        f.write(f"Python version: {python_version}\n")
        f.write(f"Platform information: {platform_info}\n")
        f.write(f"Installed packages:\n{installed_packages_str}\n")
    print(f"\nPython info also written to: {filename}\n")


# Define a function to echo the system info to the console
def echo_system_info():
    # Get the system info
    python_version, platform_info, installed_packages_str = get_system_info()
    # Print the python version
    print(f"Python version: {python_version}\n")
    # Print the platform information
    print(f"Platform information: {platform_info}\n")
    # Print the installed packages
    print(f"\nInstalled packages:\n{installed_packages_str}")


# Call the functions

echo_system_info()
write_system_info_to_file("python_info.txt")
