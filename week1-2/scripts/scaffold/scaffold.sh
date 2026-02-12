#!/bin/bash
# ============================================================
# scaffold.sh — Project Scaffolder
# Creates a new project directory with a consistent structure.
#
# Usage:  ./scaffold.sh <project-name> [--git]
# Example: ./scaffold.sh my-cool-project --git
#
# Concepts: variables, conditionals, functions, heredocs,
#           ANSI colors, exit codes, command-line arguments
# ============================================================

# ----- Configuration (edit these defaults) -------------------
DEFAULT_AUTHOR="Your Name"
GITIGNORE_EXTRAS=""          # e.g. "*.csv\ndata/"
# -------------------------------------------------------------

# ----- Color helpers (ANSI escape codes) ---------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

success() { echo -e "${GREEN}  ✓  $1${RESET}"; }
warn()    { echo -e "${YELLOW}  !  $1${RESET}"; }
error()   { echo -e "${RED}  ✗  $1${RESET}"; }

# ----- Validate arguments ------------------------------------
# $# is the number of arguments passed to the script.
if [ $# -lt 1 ]; then
    echo -e "${BOLD}Usage:${RESET} ./scaffold.sh <project-name> [--git]"
    echo "  --git   Initialize a git repository in the new project"
    exit 1    # Non-zero exit code signals an error
fi

PROJECT_NAME="$1"
INIT_GIT=false

# Check for the --git flag in any argument position
for arg in "$@"; do
    if [ "$arg" = "--git" ]; then
        INIT_GIT=true
    fi
done

# Make sure the directory doesn't already exist
if [ -d "$PROJECT_NAME" ]; then
    error "Directory '$PROJECT_NAME' already exists."
    exit 1
fi

# ----- Create the directory tree -----------------------------
# mkdir -p creates parent directories as needed and doesn't
# error if the directory already exists.
create_structure() {
    mkdir -p "$PROJECT_NAME/notes"
    mkdir -p "$PROJECT_NAME/scripts"
    mkdir -p "$PROJECT_NAME/src"
    success "Created directories"
}

# ----- Generate starter files --------------------------------
# Heredocs (cat <<EOF ... EOF) let us write multi-line file
# content inline. Variables inside are expanded automatically.
create_files() {
    local DATE
    DATE=$(date +"%Y-%m-%d")

    # README.md — project name and date are filled in automatically
    cat <<EOF > "$PROJECT_NAME/README.md"
# $PROJECT_NAME

Created on $DATE by $DEFAULT_AUTHOR.

## About

_Describe your project here._

## Getting Started

\`\`\`bash
cd $PROJECT_NAME
\`\`\`
EOF
    success "Created README.md"

    # .gitignore — sensible defaults for most projects
    cat <<EOF > "$PROJECT_NAME/.gitignore"
# OS files
.DS_Store
Thumbs.db

# Editor files
*.swp
*.swo
*~
.vscode/
.idea/

# Environment & secrets
.env
.env.local

# Dependencies
node_modules/

$GITIGNORE_EXTRAS
EOF
    success "Created .gitignore"

    # A starter notes file
    cat <<EOF > "$PROJECT_NAME/notes/ideas.md"
# Ideas & Notes

- Started project on $DATE
-
EOF
    success "Created notes/ideas.md"
}

# ----- Optional: initialize git ------------------------------
init_git() {
    if [ "$INIT_GIT" = true ]; then
        # Run git init inside the new project directory.
        # We redirect stdout to /dev/null to keep output clean.
        if git init "$PROJECT_NAME" > /dev/null 2>&1; then
            success "Initialized git repository"
        else
            warn "git init failed — is git installed?"
        fi
    fi
}

# ----- Print summary -----------------------------------------
print_summary() {
    echo ""
    echo -e "${BOLD}Project '$PROJECT_NAME' is ready!${RESET}"
    echo ""
    echo "  $PROJECT_NAME/"
    echo "  ├── README.md"
    echo "  ├── .gitignore"
    echo "  ├── notes/"
    echo "  │   └── ideas.md"
    echo "  ├── scripts/"
    echo "  └── src/"
    echo ""
    echo -e "  Next step: ${BOLD}cd $PROJECT_NAME${RESET}"
}

# ----- Run everything ----------------------------------------
echo ""
echo -e "${BOLD}Scaffolding '$PROJECT_NAME'...${RESET}"
echo ""

create_structure
create_files
init_git
print_summary
