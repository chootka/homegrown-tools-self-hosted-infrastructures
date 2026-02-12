# scaffold — Project Scaffolder

A bash script that creates a new project directory with a consistent folder structure, starter files, and optional git initialization.

## Usage

```bash
# Make it executable (you only need to do this once)
chmod +x scaffold.sh

# Create a new project
./scaffold.sh my-cool-project

# Create a new project and initialize git
./scaffold.sh my-cool-project --git
```

This creates:

```
my-cool-project/
├── README.md        ← auto-filled with project name + date
├── .gitignore       ← sensible defaults
├── notes/
│   └── ideas.md     ← a place for brainstorming
├── scripts/
└── src/
```

## Bash Concepts Walkthrough

This script is designed to teach. Here's what each section demonstrates:

### 1. Shebang line (`#!/bin/bash`)
The very first line tells the operating system which program should run this file. Without it, the system doesn't know it's a bash script.

### 2. Variables
```bash
PROJECT_NAME="$1"     # $1 is the first argument passed to the script
DEFAULT_AUTHOR="Your Name"
```
Variables in bash have no spaces around `=`. You reference them with `$` or `${...}`.

### 3. Command-line arguments
```bash
$#   # number of arguments
$1   # first argument
$@   # all arguments
```
We use `$#` to check that the user provided a project name, and loop through `$@` to look for the `--git` flag.

### 4. Conditionals
```bash
if [ $# -lt 1 ]; then
    echo "Usage: ..."
    exit 1
fi
```
`[ ... ]` is the test command. `-lt` means "less than". `-d` checks if a directory exists.

### 5. Functions
```bash
create_structure() {
    mkdir -p "$PROJECT_NAME/notes"
    # ...
}
```
Functions group related commands. They're called just by writing their name: `create_structure`.

### 6. Heredocs (`cat <<EOF`)
```bash
cat <<EOF > "$PROJECT_NAME/README.md"
# $PROJECT_NAME
Created on $DATE
EOF
```
Heredocs let you write multi-line text inline. Variables like `$PROJECT_NAME` get expanded. The text between `<<EOF` and `EOF` is piped to `cat`, which writes it to a file.

### 7. Color output (ANSI codes)
```bash
GREEN='\033[0;32m'
RESET='\033[0m'
echo -e "${GREEN}Success!${RESET}"
```
`\033[` starts an ANSI escape sequence. The `echo -e` flag tells echo to interpret these escapes. `RESET` returns to normal.

### 8. Exit codes
```bash
exit 1   # something went wrong
exit 0   # success (also the default)
```
Every command in Linux returns an exit code. `0` means success; anything else means failure. You can check the last exit code with `$?`.

### 9. Configuration
The top of the script has variables you can edit:
```bash
DEFAULT_AUTHOR="Your Name"
GITIGNORE_EXTRAS=""
```
This is a simple pattern for making scripts configurable without needing command-line flags for everything.

## Try It

1. `chmod +x scaffold.sh`
2. `./scaffold.sh test-project --git`
3. `ls -la test-project/` — see what was created
4. `cat test-project/README.md` — check the auto-generated content
5. Try modifying the script — add a new file to the template, change the folder structure, or add a new flag.

## Connection to the Course

In weeks 3–4, when we set up self-hosted servers, you'll use scripts like this to bootstrap project directories, config files, and deployment setups. Automation starts here.
