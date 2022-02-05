from pathlib import Path
import lddwrap
import argparse
import sys
import random
import os
import subprocess
import time

PROMPT = "\033[1;37mh\033[0m"

# Normal output messages
def pn(output):
    print(f"{PROMPT}\033[1;35m>>\033[0m {output}")

# Erroneous output messages
def pe(output):
    print(f"{PROMPT}\033[1;31m>>\033[0m {output}")

# Informational/Warning output messages
def pw(output):
    print(f"{PROMPT}\033[1;33m>>\033[0m {output}")

def banner():
    print("")
    print("██╗  ██╗███████╗ █████╗ ██████╗ ██╗     ███████╗███████╗███████╗")
    print("██║  ██║██╔════╝██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝██╔════╝")
    print("███████║█████╗  ███████║██║  ██║██║     █████╗  ███████╗███████╗")
    print("██╔══██║██╔══╝  ██╔══██║██║  ██║██║     ██╔══╝  ╚════██║╚════██║")
    print("██║  ██║███████╗██║  ██║██████╔╝███████╗███████╗███████║███████║")
    print("╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝╚══════╝╚══════╝")
    print("\t\t\t\tautomate your automation™\n\n")
                                                                    
def usage():
    print("OPTIONS:")
    print("-t, --target\t\t\tPath of the target ELF to analyze")
    print("-a, --analyzer\t\t\tPath to Ghidra's 'analyzeHeadless' script")
    print("-f, --folder\t\t\tName of the Ghidra project folder to create")
    print("-p, --project\t\t\tName of the Ghidra project to create")
    print("-s, --script\t\t\tScript name to run in analyzer")
    print("-d, --dependencies\t\tFind and analyze dependencies for ELF")
    print("-h, --help\t\t\tPrint this")
    print("")
    print("EXAMPLES:")
    print("usage: ./headless -t <target> -a <analyzeHeadless_path> -s <script> -d")
    print("usage: ./headless -t /usr/bin/objdump -a /home/user/Ghidra/ghidra_9.0.1/support/analyzeHeadless")
    print("usage: ./headless -t <target> -a <analyzeHeadless> -s \"MyScript.py <script_arg1> <script_arg2>\"")
    sys.exit(0)

def validate_args(args):
    # Check for required arguments
    if args.help or not args.target or not args.analyzer:
        usage()
        
    # Make sure files exist
    if not Path(args.target).is_file():
        pe(f"'{args.target}' is not a file")
        sys.exit(0)

    if not Path(args.analyzer).is_file():
        pe(f"'{args.analyzer}' is not a file")
        sys.exit(0)

def parse():
    parser = argparse.ArgumentParser(add_help = False)
    parser.add_argument("-t", "--target")
    parser.add_argument("-a", "--analyzer")
    parser.add_argument("-f", "--folder")
    parser.add_argument("-p", "--project")
    parser.add_argument("-s", "--script", action = "append")
    parser.add_argument("-d", "--dependencies", action = "store_true")
    parser.add_argument("-h", "--help", action = "store_true")

    return parser.parse_args()

# Find linked dependencies for target that have a filepath
def find_dependencies(target):
    pn(f"Locating linked dependencies for '{target}'...")
    deps = lddwrap.list_dependencies(path = Path(target))
    paths = []
    if len(deps) > 0:
        for i in range(0, len(deps)):
            if deps[i].path:
                paths.append(deps[i].path)

    if len(paths) > 0:
        pn(f"Found {len(paths)} dependencies:")
        for p in paths:
            print(f"    -- {p}")
    
    else:
        pw("Unable to find any dependencies")

    return paths

def get_tmp():
    pw(f"No project folder provided, using: '/tmp'")
    return "/tmp"

def get_rand_project_name():
    proj = "project_"
    for i in range(0, 6):
        proj += str(random.choice(range(0, 10)))

    pw(f"No project name provided, created one: '{proj}'")

    return proj

# Build the command line arg we want to send to the analyzeHeadless script
def build_cmd(args, deps):
    pn("Building command to send to the analyzeHeadless script...")

    # Add script location
    cmd = f"{args.analyzer}"

    # If we have a project folder, use it, if not make one
    folder = args.folder if args.folder else get_tmp()
    cmd = f"{cmd} {folder}"

    # If we have a project name, use it, if not make one
    proj = args.project if args.project else get_rand_project_name()
    cmd = f"{cmd} {proj}"

    # If we have deps, import them
    for path in deps:
        cmd = f"{cmd} -import {path}"

    # Add postScript location
    for script in args.script:
        # Determine if it takes args
        if len(script.split()) > 1:
            cmd = f"{cmd} -postScript \"{script}\""
        else:
            cmd = f"{cmd} -postScript {script}"

    # Display the completed command to the user
    banner_len = min(len(cmd), os.get_terminal_size().columns)
    banner = "=" * banner_len
    print("\n\033[1;37mCOMMAND\033[0m")
    print(f"\033[1;35m{banner}\033[0m")
    print(cmd)
    print(f"\033[1;35m{banner}\033[0m\n")

    return cmd

def run_cmd(cmd):
    answer = input(f"{PROMPT}\033[1;35m>>\033[0m Run this command? (Y/N) ")
    if answer.lower() != "y":
        sys.exit(0)

    # Create a log file to capture the analyzeHeadless output
    log_id = ""
    for n in range(0, 6):
        log_id += str(random.choice(range(0, 10)))
    log = f"/tmp/{log_id}_headless_log.txt"
    try:
        with open(log, "w+") as f:
            f.close()
        pn(f"Created log file '{log}'")
    except Exception as e:
        pe(f"Unable to create log file {log}, err: {e}")

    # Add redirection to log file
    cmd = f"{cmd} > {log} 2>&1"

    pn("Running command, analysis might take a while!")
    start = time.time()
    p = subprocess.Popen(cmd, shell=True)
    p.wait()
    elapsed = int(time.time() - start)

    pn(f"Analyzer exited with code: {p.returncode}")
    pn(f"Analysis complete, elapsed (sec): {elapsed}")
    pn(f"Check {log} for details")

def main():
    banner()
    args = parse()
    validate_args(args)

    if args.dependencies:
        deps = find_dependencies(args.target)

    cmd = build_cmd(args, deps)

    run_cmd(cmd)


if __name__ == "__main__":
    main()
