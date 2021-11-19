#!/usr/bin/env python3

import os
import pathlib
import platform
import shutil
import subprocess
import sys
from zipfile import ZipFile


#
#   Constants
#
cwd = os.path.dirname(os.path.realpath(__file__))
descript_electron_fork = 'git@github.com:descriptinc/electron.git'
electron_build_tools_module = '@electron/build-tools'


#
#
#
def readVersion() -> str:
    """
    Read the version string from ../ELECTRON_VERSION
    :return: the electron version
    """
    result = ''
    with open(os.path.join(os.path.dirname(cwd), 'ELECTRON_VERSION')) as f:
        lines = f.readlines()
        for line in lines:
            result = line.strip()
            break
    return result


#
#
#
def getProcessorArch() -> str:
    """
    Gets the current processor architecture
    :return: `'x64'` or `'arm64'`
    """ 
    result = platform.machine()
    if result == 'x86_64':
        result = 'x64'
    return result

#
#
#
def installElectronBuildTools(log_file):
    """
    Installs electron build tools
    See https://github.com/electron/build-tools
    """
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
#
#
def getElectronBuildToolsPath(log_file, throw_if_not_found = True) -> str:
    """
    Checks for the existance of the electron build tools
    if not installed, tries to install the build tools once
    and will throw if still not found
    See https://github.com/electron/build-tools
    
    :return: path to electron build tools
    """
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
#
#
def getElectronBuildConfiguration(log_file, build_tools) -> str:
    """
    Get Build Configuration
    :return: `root` folder for current Electron Build Configuration
    """
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
    """
    Redirects the git remote origin back to the specified fork
    (as opposed to the official electron repo)
    """
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
#
#
def synchronizeCode(log_file, build_tools):
    """
    Calls `e sync` which calls `gclient` under the hood
    See https://www.chromium.org/developers/how-tos/depottools
    """
    log_file.write('\nSyncing Code\n')
    log_file.write('=======================\n')

    args = [build_tools, 'sync', '-vvvv']
    log_file.write(f"{' '.join(args)}\n")
    log_file.flush()
    subprocess.run(args, stdout=log_file, stderr=log_file, check=True)


#
#
#
def buildElectron(log_file, build_tools):
    """
    Build Electron which calls `ninja` under the hood
    See https://ninja-build.org
    """
    log_file.write('\nBuilding Electron\n')
    log_file.write('=======================\n')

    args = [build_tools, 'build', 'electron:dist', '-v']
    log_file.write(f"{' '.join(args)}\n")
    log_file.flush()
    subprocess.run(args, stdout=log_file, stderr=log_file, check=True)


#
#
#
def verifyElectronExecutable(log_file, build_tools) -> str:
    """
    Verifies the built executable exists
    and launches it to grab the version
    :return: the path to the output dir
    """
    log_file.write('\nChecking Electron Executable\n')
    log_file.write('=======================\n')

    args = [build_tools, 'show', 'outdir']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    result = output.decode('utf-8').strip()
    log_file.write(f"{result}n")

    args = [build_tools, 'show', 'exe']
    log_file.write(f"{' '.join(args)}\n")
    output = subprocess.check_output(args)
    exe = output.decode('utf-8').strip()
    log_file.write(f"{exe}\n")

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
def generateChecksum(output_folder):
    """
    Calculates checksums for every file in `output_folder`
    """

    checksums = set()

    # calculate checksums for all files
    for (dirpath, dirnames, filenames) in os.walk(output_folder):
        for file in filenames:
            args = ['shasum', '-a', '256', os.path.join(dirpath, file)]
            output = subprocess.check_output(args)
            checksum = output.decode('utf-8').strip()

            # replace absolute path to just filename
            # From: '0a88d3f97f356c6a42449fd548f9b586f565899144849019014e36c7683b745e  /Users/cvanwink/Source/git/electron/src/out/Testing/dist.zip'
            # To:   '0a88d3f97f356c6a42449fd548f9b586f565899144849019014e36c7683b745e  *electron-v13.1.6-darwin-x64.zip'
            checksum = checksum.replace(os.path.join(dirpath, ''), '*')
            checksums.add(checksum)
    
    # Write Checksums to file
    checksum_file_path = os.path.join(output_folder, 'SHAMSUM256.txt')
    checksum_file = open(checksum_file_path, 'w')
    for checksum in checksums:
        checksum_file.write(f'{checksum}\n')
    checksum_file.close()


#
#
#
def copyElectronDistribution(log_file, src, dest) -> str:
    """
    Copies the electron distribution zip
    to our output folder and calculates a checksum
    and places that in the output folder as well
    :return: the path the the destination zip file
    """
    log_file.write('\nCopying Electron Distribution\n')
    log_file.write('=======================\n')

    # Copy dist.zip
    src_file = os.path.join(src, 'dist.zip')
    dest_file = os.path.join(dest, f'electron-v{readVersion()}-{sys.platform}-{getProcessorArch()}.zip')
    log_file.write(f'Copying {src_file} --> {dest_file}\n')
    shutil.copy2(src_file, dest_file)

    return dest_file


#
#
#
def symbolNameFromFile(pe_file) -> str:
    """
    Returns the name for the symbol file which should be
    generated for any particular pe_file, taking into account
    files which are inside packages like `.app`, `.framework`, `.bundle`, etc
    """
    result = os.path.basename(pe_file)
    file_ref = pathlib.Path(pe_file)
    pe_path_parts = file_ref.parts

    known_bundles = ['app', 'framework', 'bundle']
    for bundle_type in known_bundles:
        try:
            bundle_name = f'{file_ref.stem}.{bundle_type}'
            bundle_index = pe_path_parts.index(bundle_name)
            result = bundle_name
            break
        except ValueError as e:
            continue
    return result + '.dSYM'

#
#
#
def packageSymbols(log_file, dest):
    """
    Finds all of the symbols in `src`
    and zips them into a single .zip in `dest`
    :param: dest -- the output folder for the symbols zip
    """
    log_file.write('\nBundling Symbol Files\n')
    log_file.write('=======================\n')
    
    # get executable path
    args = ['e', 'show', 'exe']
    output = subprocess.check_output(args)
    exe_path = output.decode('utf-8').strip()
    try:
        # get parent .app bundle from path
        exe_ref = pathlib.Path(exe_path)
        exe_path_parts = exe_ref.parts
        app_bundle_index = exe_path_parts.index(f'{exe_ref.stem}.app')
        exe_path_parts = exe_path_parts[:app_bundle_index + 1]
        exe_path = os.path.join(*exe_path_parts)
    except ValueError as e:
        raise e

    # scan executable path for all PE files
    pe_files = set()
    for (dirpath, dirnames, filenames) in os.walk(exe_path):
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            if not os.path.islink(file_path):
                args = ['file', '-b', file_path]
                output = subprocess.check_output(args)
                file_type = output.decode('utf-8').strip()
                if file_type.startswith('Mach-O'):
                    log_file.write(f'{file_path}\t{file_type}\n')
                    pe_files.add(file_path)

    symbol_temp_folder = os.path.join(dest, 'symbol_temp')
    if (os.path.exists(symbol_temp_folder)):
        shutil.rmtree(symbol_temp_folder)
    os.makedirs(symbol_temp_folder)

    # generate a symbol for each PE file
    symbol_files = set()
    for pe_file in sorted(pe_files, key=lambda s: str(s).lower()):
        symbol_path = os.path.join(symbol_temp_folder, symbolNameFromFile(pe_file))
        args = ['dsymutil', os.path.normpath(pe_file), '-o', os.path.normpath(symbol_path)]
        log_file.write(f"{' '.join(args)}\n")
        log_file.flush()
        subprocess.run(args, stdout=log_file, stderr=log_file, check=True)
        symbol_files.add(symbol_path)
    
    # zip each symbol file
    dest_file = os.path.join(dest, f'electron-v{readVersion()}-{sys.platform}-{getProcessorArch()}-symbols')
    log_file.write(f'Creating {dest_file}.zip\n')
    shutil.make_archive(dest_file, 'zip', symbol_temp_folder)
    
    shutil.rmtree(symbol_temp_folder)

#
#
#
def main():
    output_dir = os.path.join(cwd, 'out')
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)

    # change to directory of script
    os.chdir(cwd)

    # create a log file for archival purposes
    log_file_name = f'electron-v{readVersion()}-{sys.platform}-{getProcessorArch()}-log.txt'
    log_file_path = os.path.join(output_dir, log_file_name)
    build_electron_log_file = open(log_file_path, 'w')

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

    build_dir = verifyElectronExecutable(build_electron_log_file, build_tools)

    electron_zip = copyElectronDistribution(build_electron_log_file, build_dir, output_dir)

    packageSymbols(build_electron_log_file, output_dir)

    build_electron_log_file.write('\nEnd of build-electron.py\n')
    build_electron_log_file.write('=======================\n')
    build_electron_log_file.close()

    # zip up log file
    with ZipFile(os.path.splitext(log_file_path)[0] + '.zip', 'w') as myzip:
        myzip.write(log_file_path, os.path.basename(log_file_path))
    os.remove(log_file_path)

    generateChecksum(output_dir)


#
#   entry
#
if __name__ == '__main__':
    main()
