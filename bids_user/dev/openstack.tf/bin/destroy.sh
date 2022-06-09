#!/usr/bin/env bash

CURRENT_DIR="$(pwd)"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [[ ! -f "${DIR}/set-env.sh" ]] ; then
  echo "cannot find ${DIR}/set-env.sh file"
  exit -1
fi
cd "${DIR}/.." && source ./bin/set-env.sh

mkdir -p "${DIR}/../.terraform"
set TF_LOG=INFO
set TF_LOG_PATH="${DIR}/../.terraform/destroy.sh.log"

function remove_crewportal_openstack_resources {
  openstack keypair delete ib6-sas-keypair || echo 'cannot delete keypair'
  for id in $(openstack server list | grep -w 'ib6-sas' | awk '{ print $2 }') ; do
    echo "delete openstack server with id ${id}"
    openstack server delete ${id} || echo 'cannot delete server'
  done
}

# main
remove_crewportal_openstack_resources

cd "${CURRENT_DIR}"
