## Shell commands

The Bash tool runs zsh, not bash. `~/.config/zsh/.zshenv` (from the dotfiles repo) sets `sh_word_split` and `ksh_arrays` in agent shells, so unquoted variables split into words, arrays count from 0, and `$var:x` and `$var[x]` are plain text, as in bash. If `W="echo ok"; $W` fails with `command not found: echo ok`, those options are missing in that shell: run bash-style commands as `bash -c '...'`.

What stays zsh either way:

- A pipeline's exit codes are in `${pipestatus[0]}`, `${pipestatus[1]}` and so on. `PIPESTATUS` is always empty, so `echo "exit: ${PIPESTATUS[0]}"` prints no code. To fail on any stage, use `set -o pipefail`.
- `status` is read-only and `path` is tied to `PATH`. Never use either as a variable name.
- `mapfile`, `readarray`, `read -a`, `${!var}`, `${var^^}`, `${var,,}` and `BASH_REMATCH` do not exist. Run a command that needs one as `/opt/homebrew/bin/bash -c '...'` (bash 5; macOS `/bin/bash` is 3.2, without `mapfile` or `${var^^}`).
