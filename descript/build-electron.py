#!/usr/bin/env python3

import os
import platform
import shutil
import subprocess
import sys

#
#   Constants
#
cwd = os.path.dirname(os.path.realpath(__file__))


#
#   Read the version string from ../ELECTRON_VERSION
#   @return the electron version
#
def readVersion() -> str:
    result = ''
    with open(os.path.join(os.path.dirname(cwd), 'ELECTRON_VERSION')) as f:
        lines = f.readlines()
        for line in lines:
            result = line.strip()
            break
    return result


#
#   Checks for the existance of the electron build tools
#   @return path to electron build tools
#
def getElectronBuildToolsPath(log_file) -> str:
    result = ''
    
    log_file.write('\nChecking for Electron Build Tools\n')
    log_file.write('=======================\n')
    args = ['/usr/bin/which', 'e']
    log_file.write(f"{' '.join(args)}\n")
    try:
        output = subprocess.check_output(args)
        result = output.decode('utf-8').strip()
        log_file.write(f'{result}\n')
    except subprocess.CalledProcessError as e:
        log_file.write('Error: Electron Build Tools not Installed!\n')
        log_file.write('See: https://github.com/electron/build-tools')
        raise(e)
    
    return result

#
#   Get Build Configuration
#   @return root
#
def getElectronBuildConfiguration(log_file, build_tools) -> str:
    log_file.write('\nChecking Electron Build Configuration\n')
    log_file.write('=======================\n')

    args = [build_tools, 'show', 'current']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    args = [build_tools, 'show', 'root']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    root = output.decode('utf-8').strip()
    log_file.write(f"{root}\n")

    return root

#
#
#
def main():
    log_dir = os.path.join(cwd, 'logs')
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

    # create a log file for archival purposes
    log_file_name = f'build-electron-{readVersion()}-{sys.platform}-{platform.machine()}.log.txt'
    build_electron_log_file = open(os.path.join(log_dir, log_file_name), 'w')

    build_electron_log_file.write('Begin build-electron.py\n')
    build_electron_log_file.write('=======================\n')

    build_tools = getElectronBuildToolsPath(build_electron_log_file)

    root = getElectronBuildConfiguration(build_electron_log_file, build_tools)

    build_electron_log_file.write('\nEnd of build-electron.py\n')
    build_electron_log_file.write('=======================\n')
    build_electron_log_file.close()


#
#   entry
#
if __name__ == '__main__':
    main()
