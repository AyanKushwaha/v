#!/usr/bin/env bash
# Start launcher from given host
# First argument is the hostname of the session server host, ex cweutcmsst01.flysas.com:
# Second argument is optional and specifies the port to use, default is 8443.
set -e

if [ -z "${1}" ]
then
  echo -e "Usage:\n  $0 <session server hostname>\n  $0 <session server hostname> <port>"
  echo -e "Ex:\n  $0 cweutcmsst01.flysas.com\n  $0 cweutcmsst01.flysas.com 8444"
  exit 1
fi

if [ -z "${DISPLAY}" ]
then
  echo -e "No DISPLAY set. Launcher requires X11. Exiting."
  exit 1
fi

if [ -z "${2}" ]
then
  port="8443"
else
  port="${2}"
fi


sessionserver_host="${1}"
cache_dir="${HOME}/.cache/cms_launcher/${sessionserver_host}_${port}"
jar_name="launcherdownloader.jar"
appbase="https://${sessionserver_host}:${port}/jws/"
# Ensure correct version of java is selected by putting it first in the PATH
PATH="/usr/lib/jvm/jdk-11.0.2/bin/:${PATH}"


mkdir -p ${cache_dir}
if ! output=$(wget ${appbase}${jar_name} -O ${cache_dir}/${jar_name} 2>&1)
then
  echo -e "Download of launcher jar-file failed. Output:\n${output}"
  exit 1
fi
java -Dlauncherdownloader.appbase=${appbase} -jar ${cache_dir}/${jar_name} >> ${cache_dir}/launcher.log 2>&1
echo "Starting Launcher from ${sessionserver_host}:${port}"
