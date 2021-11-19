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
electron_build_tools_module = '@electron/build-tools'


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
    #args = ['npm', 'i', '-g', 'electron_build_tools_module']

    args = ['yarn', 'global', 'add', f'{electron_build_tools_module}@1.0.4']
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
#   @return the path to the output dir
#
def verifyElectronExecutable(log_file, build_tools) -> str:
    log_file.write('\nChecking Electron Executable\n')
    log_file.write('=======================\n')

    args = [build_tools, 'show', 'outdir']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    result = output.decode('utf-8').strip()
    log_file.write(f"{result}\n\n")

    args = [build_tools, 'show', 'exe']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    exe = output.decode('utf-8').strip()
    log_file.write(f"{exe}\n\n")

    # launch and print version
    args = [exe, '-v']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    # launch and print Node ABI Version
    args = [exe, '-a']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    log_file.write(f"{output.decode('utf-8')}\n")

    return result


#
#
#
def copyElectronDistribution(log_file, src, dest):
    log_file.write('\nCopying Electron Distribution\n')
    log_file.write('=======================\n')

    if not os.path.exists(dest):
        os.makedirs(dest)

    arch = platform.machine()
    if arch == 'x86_64':
        arch = 'x64'

    src_file = os.path.join(src, 'dist.zip')
    dest_file = os.path.join(dest, f'electron-v{readVersion()}-{sys.platform}-{arch}.zip')

    log_file.write(f'{src_file} --> {dest_file}\n')
    shutil.copy2(src_file, dest_file)

    # shasum -a 256 dist.zip
    # 9bdc192adbe6839056b97f1eace2103479c47260311a37117f95ce64b31b6576 *electron-v13.1.6-darwin-x64.zip
    # SHASUMS256.txt

    # symbols
    # dest_file-symbols.zip
    # cp -r PATH_TO_ELECTRON_OUT/Release/**/*.dSYM PATH_TO_SYMBOLS_FOLDER

#
#
#
def main():
    log_dir = os.path.join(cwd, 'logs')
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    os.makedirs(log_dir)

    # change to directory of script
    os.chdir(cwd)

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

    output_dir = verifyElectronExecutable(build_electron_log_file, build_tools)

    copyElectronDistribution(build_electron_log_file, output_dir, os.path.join(cwd, 'out'))

    build_electron_log_file.write('\nEnd of build-electron.py\n')
    build_electron_log_file.write('=======================\n')
    build_electron_log_file.close()


#
#   entry
#
if __name__ == '__main__':
    main()
