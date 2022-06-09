#!/bin/sh
# Checks for branches that either are or aren't merged to 
# default and that aren't yet closed.

script=`basename $0`
usage="usage: $script [-n --not-merged] [-u --username <your_username>]"

# Options
NOT_MERGED=false
USERNAME=
HELP=false

while true; do
  case "$1" in
    -n | --not-merged ) NOT_MERGED=true; shift ;;
    -u | --username ) USERNAME="$2"; shift 2 ;;
    -h | --help    ) HELP=true; shift ;;
    * ) break ;;
  esac
done

print_usage ( )
{
    cat <<__tac__
$usage

OPTIONS
    -n --not-merged Optional: Defaults to false, which checks for merged branches that aren't closed

    -u --username   Optional: If specified only outputs relevant branches for specified user  

__tac__
}

cmd ( )
{
  if [[ "$NOT_MERGED" = "true" ]]; then
    echo "Checking for open branches not yet merged w. default"
    hg log -r "not ancestors(heads(default)) and head() and not closed()"
  else
    echo "Checking for open branches merged w. default" 
    hg log -r "ancestors(heads(default)) and head() and not closed()"
  fi
}


IN_REPO=$(hg branch 2> /dev/null)

if [[ -z "$IN_REPO" ]]; then
  echo "Not possible to execute $script outside of an Mercurial repository"
  exit 1
elif [[ "$HELP" = "true" ]]; then
  print_usage
  exit 0
elif [[ -z "$USERNAME" ]]; then 
  cmd
else
  cmd | grep -i "$USERNAME" -B 3 -A 3
fi

