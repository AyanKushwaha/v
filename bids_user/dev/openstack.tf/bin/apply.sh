#!/bin/bash

CURRENT_DIR="$(pwd)"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [[ ! -f "${DIR}/set-env.sh" ]] ; then
  echo "cannot find ${DIR}/set-env.sh file"
  exit -1
fi
cd "${DIR}/.." && source ./bin/set-env.sh

mkdir -p "${DIR}/../.terraform"
set TF_LOG=INFO
set TF_LOG_PATH="${DIR}/../.terraform/apply.sh.log"
# https://www.terraform.io/docs/internals/debugging.html

cd "${DIR}/.." && terraform apply -input=false -auto-approve

cd "${CURRENT_DIR}"
