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
descript_electron_fork = 'git@github.com:descriptinc/electron.git'


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
#   Installs electron build tools
#   See https://github.com/electron/build-tools
#
def installElectronBuildTools(log_file):
    log_file.write('\nInstalling Electron Build Tools\n')
    log_file.write('=======================\n')
    
    # the following is what is listed on the build-tools page
    # but doesn't work, so we'll use yarn instead of npm
    #args = ['npm', 'i', '-g', '@electron/build-tools']

    args = ['yarn', 'global', 'add', '@electron/build-tools@1.0.4']
    log_file.write(f"{' '.join(args)}\n")
    log_file.flush()
    subprocess.run(args, stdout=log_file, stderr=log_file, check=True)


#
#   Checks for the existance of the electron build tools
#   if not installed, tries to install the build tools once
#   and will throw if still not found
#   See https://github.com/electron/build-tools
#   @return path to electron build tools
#
def getElectronBuildToolsPath(log_file, throw_if_not_found = True) -> str:
    result = ''
    
    log_file.write('\nChecking for Electron Build Tools\n')
    log_file.write('=======================\n')
    args = ['which', 'e']
    log_file.write(f"{' '.join(args)}\n")
    try:
        output = subprocess.check_output(args)
        result = output.decode('utf-8').strip()
        log_file.write(f'{result}\n')
    except subprocess.CalledProcessError as e:
        log_file.write('Error: Electron Build Tools not Installed!\n')
        log_file.write('See: https://github.com/electron/build-tools\n')

        if throw_if_not_found:
            installElectronBuildTools(log_file)
            result = getElectronBuildToolsPath(log_file, False)
        
        if throw_if_not_found and not len(result):
            raise(e)
    
    return result


#
#   Get Build Configuration
#   @return root
#
def getElectronBuildConfiguration(log_file, build_tools) -> str:
    log_file.write('\nChecking Electron Build Configuration\n')
    log_file.write('=======================\n')

    args = [build_tools, 'show', 'root']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    root = output.decode('utf-8').strip()
    log_file.write(f"{root}\n\n")

    args = [build_tools, 'show', 'current']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    args = [build_tools, 'show', 'depotdir']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    args = [build_tools, 'show', 'env']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    return root


#
#
#
def redirectGitOrigin(log_file, fork):
    log_file.write(f'\nRedirecting Git origin to: {fork}\n')
    log_file.write('=======================\n')

    args = ['git', 'remote', 'set-url', 'origin', fork]
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    args = ['git', 'remote', 'set-url', '--push', 'origin', fork]
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")
    
    # Verify results
    args = ['git', 'remote', '-v']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")


#
#   Calls `e sync` which calls `gclient` under the hood
#   See https://www.chromium.org/developers/how-tos/depottools
#
def synchronizeCode(log_file, build_tools):
    log_file.write('\nSyncing Code\n')
    log_file.write('=======================\n')

    args = [build_tools, 'sync', '-vvvv']
    log_file.write(f"{' '.join(args)}\n")
    log_file.flush()
    subprocess.run(args, stdout=log_file, stderr=log_file, check=True)


#
#   Build Electron which calls 'ninja' under the hood
#   See https://ninja-build.org
#
def buildElectron(log_file, build_tools):
    log_file.write('\nBuilding Electron\n')
    log_file.write('=======================\n')

    args = [build_tools, 'build', 'electron:dist', '-v']
    log_file.write(f"{' '.join(args)}\n")
    log_file.flush()
    subprocess.run(args, stdout=log_file, stderr=log_file, check=True)


#
#   Verifies the built executable exists
#   and launches it to grab the version
#   @return the path to the built executable
#
def verifyElectronExecutable(log_file, build_tools) -> str:
    log_file.write('\nChecking Electron Executable\n')
    log_file.write('=======================\n')

    args = [build_tools, 'show', 'exe']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    result = output.decode('utf-8').strip()
    log_file.write(f"{result}\n\n")

    # launch and print version
    args = [result, '-v']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    # launch and print Node ABI Version
    args = [result, '-a']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    return result


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

    synchronizeCode(build_electron_log_file, build_tools)

    redirectGitOrigin(build_electron_log_file, descript_electron_fork)

    # Switch to root directory of tree
    # otherwise certain build commands fail
    os.chdir(root)

    buildElectron(build_electron_log_file, build_tools)

    verifyElectronExecutable(build_electron_log_file, build_tools)

    build_electron_log_file.write('\nEnd of build-electron.py\n')
    build_electron_log_file.write('=======================\n')
    build_electron_log_file.close()


#
#   entry
#
if __name__ == '__main__':
    main()
