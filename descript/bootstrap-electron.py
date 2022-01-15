#!/usr/bin/env python3

import os
import platform
import shutil
import subprocess
import sys


#
#   Constants
#
descript_electron_fork = 'https://github.com/descriptinc/electron.git'
descript_electron_fork_ssh = 'git@github.com:descriptinc/electron.git'
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
def initializeElectronSource(force = False):
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

    print ('\nInitialize Electron configuration:')
    print ('For more information, see `e init` here: https://github.com/electron/build-tools')
    print ('`release` is the default, but could be used to maintain both testings/release builds.')
    config = input('\nPlease enter the name of the desired build configuration. [release]:  ')
    if not len(config):
        config = 'release'

    args = ['e', 'init', config, '-i', config]
    if (force):
        args.append('--force')

    args.extend(['--root', path])
    
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
    should_offer_override_once = True
    while not len(root):
        args = ['e', 'show', 'root']
        print(f"\n{' '.join(args)}")
        try:
            output = subprocess.check_output(args)
            root = output.decode('utf-8').strip()
            if should_offer_override_once:
                override = input(f'\nFound root at {root}. Override? [N]:  ')
                if len(override) and override.lower() == 'y':
                    should_offer_override_once = False
                    initializeElectronSource(force=True)
                    root = ''
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

    env = os.environ
    if platform.machine() == 'arm64':
        # https://bugs.chromium.org/p/chromium/issues/detail?id=1103236
        env['VPYTHON_BYPASS'] = 'manually managed python not supported by chrome operations'

    args = ['e', 'sync', '-vvvv']
    print(f"{' '.join(args)}\n")
    subprocess.run(args, check=True, env=env)


#
#   @return the path to the electron submodule folder
#
def getElectronSubmodulePath(root) -> str:
    return os.path.join(root, 'src', 'electron')


#
#   Queries the user for a custom fork for electron
#   Defaults to Descript's custom fork
#
def getCustomElectronFork(electron_path) -> str:
    print(f'\nChoose a custom Electron Fork')
    print('=======================')

    forks = [
        descript_electron_fork,
        descript_electron_fork_ssh
        ]

    i = 0
    for fork in forks:
        print (f'[{i}]\t{fork}')
        i += 1
    print (f'[{i}]\t(Custom)')
    custom_fork_index = i

    fork = ''
    while not len(fork):
        fork = input(f'\nPlease input desired fork [0]:  ')
        if not len(fork):
            fork = descript_electron_fork
        elif not fork.isnumeric():
            fork = ''
            continue
        else:
            fork_index = int(fork)
            if (fork_index < 0) or (custom_fork_index < fork_index):
                # out of range 
                fork = ''
            elif fork_index < i:
                fork = forks[fork_index]
            elif fork_index == custom_fork_index:
                # custom fork
                fork = input(f"\nPlease input desired fork (e.g. '{descript_electron_fork}'):  ")
            
    return fork

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

    args = ['git', 'fetch']
    print(f"\n{' '.join(args)}")
    subprocess.run(args, check=True)

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

    synchronizeCode()

    electron_submodule_path = getElectronSubmodulePath(root)

    custom_fork = getCustomElectronFork(electron_submodule_path)

    # switch the electron submodule to our fork
    # this needs to be done after calling synchronizeCode()
    redirectGitOrigin(electron_submodule_path, custom_fork)

    fetchAndPullGit(electron_submodule_path, custom_fork)

    print('\nEnd of bootstrap-electron.py')
    print('=======================')


#
#   entry
#
if __name__ == '__main__':
    main()
