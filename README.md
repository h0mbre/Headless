![](/headless.png)

# Headless
Wrapper around Ghidra's analyzeHeadless script, could be helpful to some? Don't tell me anything is wrong with it, it works on my machine.

# OPTIONS:
-t, --target                    Path of the target ELF to analyze
-a, --analyzer                  Path to Ghidra's 'analyzeHeadless' script
-f, --folder                    Name of the Ghidra project folder to create
-p, --project                   Name of the Ghidra project to create
-s, --script                    Script name to run in analyzer
-d, --dependencies              Find and analyze dependencies for ELF
-h, --help                      Print this

# EXAMPLES:
usage: ./headless -t <target> -a <analyzeHeadless_path> -s <script> -d
usage: ./headless -t /usr/bin/objdump -a /home/user/Ghidra/ghidra_9.0.1/support/analyzeHeadless
usage: ./headless -t <target> -a <analyzeHeadless> -s "MyScript.py <script_arg1> <script_arg2>"
usage: ./headless -t <target> -a <analyzeHeadless> -s "MyScript.py <script_arg1> <script_arg2>" -s MyScript2.py
