#!/usr/bin/env bash

# This wrapper script is called by xTerm from Launcher. See etc/applications/application_xterm.xml
# It's purpose is to allow users to drop out of CMS shell by 'exit'-ing.

echo
echo "Entering CMS shell ...  (Do 'exit' for standard bash shell)"
echo

# Go to the carmusr base directory
cd "$(readlink -f "$(dirname $0)/..")"

# Enter CMS shell
bash bin/cmsshell

# The following only executes after and 'exit' from the previous command
unset CARMUSR
unset CARMSYS
unset CARMDATA
unset CARMTMP

# Run a "standard" shell
bash
