#!/bin/sh
# Keep the original command's output and exit status. Never log its arguments.
kind=$1
shift
"$@"
result=$?
if [ -n "$(git config --local --get learning.notebook 2>/dev/null)" ]; then
  learning_python=$(git config --local --get learning.python)
  "$learning_python" scripts/learning.py record --kind "$kind" --exit-code "$result" ||
    printf '%s\n' 'Learning capture failed; the command result was preserved.' >&2
fi
exit "$result"
