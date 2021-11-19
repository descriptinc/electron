#!/usr/bin/env python3

import os
import platform
import shutil
import subprocess
import sys


#
#   Constants
#
descript_electron_fork = 'git@github.com:descriptinc/electron.git'
descript_default_branch = 'release/15.3.1/libuv-use-posix-spawn.0'


#
#   Installs electron build tools
#   See https://github.com/electron/build-tools
#
def installElectronBuildTools():
    print('\nInstalling Electron Build Tools')
    print('=======================')
    
    # the following is what is listed on the build-tools page
    # but doesn't work, so we'll use yarn instead of npm
    #args = ['npm', 'i', '-g', '@electron/build-tools']

    args = ['yarn', 'global', 'add', '@electron/build-tools@1.0.4']
    print(f"{' '.join(args)}")
    subprocess.run(args, check=True)


#
#   Checks for the existance of the electron build tools
#   if not installed, tries to install the build tools once
#   and will throw if still not found
#   See https://github.com/electron/build-tools
#   @return path to electron build tools
#
def setupElectronBuildTools(throw_if_not_found = True) -> str:
    result = ''
    
    print('\nChecking for Electron Build Tools')
    print('=======================')
    args = ['which', 'e']
    print(f"{' '.join(args)}")
    try:
        output = subprocess.check_output(args)
        result = output.decode('utf-8').strip()
        print(f'{result}')
    except subprocess.CalledProcessError as e:
        print('Error: Electron Build Tools not Installed!')
        print('See: https://github.com/electron/build-tools')

        if throw_if_not_found:
            installElectronBuildTools()
            result = setupElectronBuildTools(False)
        
        if throw_if_not_found and not len(result):
            raise(e)
    
    return result


#
#   Initializes a root for Electron's source
#
def initializeElectronSource():
    print('\nInitialize Build Configuration')
    print('=======================')

    path = ''
    while not len(path):
        path = input('\nPlease input desired location of Electron source [~/electron]:  ')
        if not len(path):
            path = '~/electron'
        path = os.path.expanduser(path)
        try:
            os.makedirs(path)
        except FileExistsError as e:
            overwrite = input(f"'{path}' already exists, overwrite? [Y]:  ")
            if not len(overwrite) or overwrite.lower() == 'y':
                shutil.rmtree(path)
            else:
                path =''

    config = input('\nPlease enter the name of the desired build configuration [testing]:  ')
    if not len(config):
        config = 'testing'

    args = ['e', 'init', '--root', path, config]
    print(f"\n{' '.join(args)}")
    subprocess.run(args, check=True)

#
#   Setup and Print Build Configuration
#   @return root
#
def setupElectronBuildConfiguration() -> str:
    print('\nChecking Electron Build Configuration')
    print('=======================')

    root = ''
    while not len(root):
        args = ['e', 'show', 'root']
        print(f"\n{' '.join(args)}")
        try:
            output = subprocess.check_output(args)
            root = output.decode('utf-8').strip()
            print(f"{root}")
        except subprocess.CalledProcessError as e:
            initializeElectronSource()
            root = ''

    args = ['e', 'show', 'current']
    print(f"\n{' '.join(args)}")
    output = subprocess.run(args, check=True)

    args = ['e', 'show', 'depotdir']
    print(f"\n{' '.join(args)}")
    subprocess.run(args, check=True)

    args = ['e', 'show', 'env']
    print(f"\n{' '.join(args)}")
    subprocess.run(args, check=True)

    return root


#
#   Calls `e sync` which calls `gclient` under the hood
#   See https://www.chromium.org/developers/how-tos/depottools
#
def synchronizeCode():
    print('\nSyncing Code')
    print('=======================')

    args = ['e', 'sync', '-vvvv']
    print(f"{' '.join(args)}\n")
    subprocess.run(args, check=True)


#
#   @return the path to the electron submodule folder
#
def getElectronSubmodulePath(root) -> str:
    return os.path.join(root, 'src', 'electron')

#
#   Switches the git origin to specified fork
#
def redirectGitOrigin(electron_path, fork):
    print(f'\nRedirecting electron Git origin to: {fork}')
    print('=======================')

    os.chdir(electron_path)

    args = ['git', 'remote', 'set-url', 'origin', fork]
    print(f"\n{' '.join(args)}")
    subprocess.run(args, check=True)

    args = ['git', 'remote', 'set-url', '--push', 'origin', fork]
    print(f"\n{' '.join(args)}")
    subprocess.run(args, check=True)
    
    # Verify results
    args = ['git', 'remote', '-v']
    print(f"\n{' '.join(args)}")
    subprocess.run(args, check=True)

#
#   Pull
#
def fetchAndPullGit(electron_path, fork):
    print(f'\nFetching and pulling from {fork}')
    print('=======================')

    os.chdir(electron_path)

    branch = ''
    while not len(branch):
        branch = input(f'\nPlease input desired branch to checkout [{descript_default_branch}]:  ')
        if not len(branch):
            branch = descript_default_branch
        try:
            args = ['git', 'show-branch', f'remotes/origin/{branch}']
            print(f"\n{' '.join(args)}")
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as e:
            branch = ''

    args = ['git', 'checkout', branch]
    print(f"\n{' '.join(args)}")
    subprocess.run(args, check=True)

#
#
#
def main():
    print('Begin build-electron.py')
    print('=======================')

    setupElectronBuildTools()

    root = setupElectronBuildConfiguration()

    #synchronizeCode()

    electron_submodule_path = getElectronSubmodulePath(root)

    # switch the electron submodule to our fork
    # this needs to be done after calling synchronizeCode()
    redirectGitOrigin(electron_submodule_path, descript_electron_fork)

    fetchAndPullGit(electron_submodule_path, descript_electron_fork)

    print('\nEnd of build-electron.py')
    print('=======================')


#
#   entry
#
if __name__ == '__main__':
    main()
