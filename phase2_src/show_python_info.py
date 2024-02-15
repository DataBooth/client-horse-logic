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
import pkg_resources


# Define a function to get the python version, platform information and installed packages
def get_system_info():
    # Get the python version
    python_version = sys.version
    # Get the platform information
    platform_info = platform.platform()
    # Get the installed packages
    installed_packages = [f"\n{str(d)}" for d in pkg_resources.working_set]
    # Return a tuple of the results
    return (python_version, platform_info, installed_packages)


# Define a function to write the system info to a text file
def write_system_info_to_file(filename):
    # Open the file in write mode
    with open(filename, "w") as f:
        # Get the system info
        system_info = get_system_info()
        # Write the python version
        f.write(f"Python version: {system_info[0]}\n")
        # Write the platform information
        f.write(f"Platform information: {system_info[1]}\n")
        # Write the installed packages
        f.write(f"Installed packages: {', '.join(system_info[2])}\n")
    print(f"\nPython info also written to: {filename}\n")


# Define a function to echo the system info to the console
def echo_system_info():
    # Get the system info
    system_info = get_system_info()
    # Print the python version
    print(f"Python version: {system_info[0]}")
    # Print the platform information
    print(f"Platform information: {system_info[1]}")
    # Print the installed packages
    print(f"Installed packages: {', '.join(system_info[2])}")


# Call the functions

echo_system_info()
write_system_info_to_file("python_info.txt")
