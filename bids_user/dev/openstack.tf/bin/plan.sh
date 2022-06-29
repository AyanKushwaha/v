#!/bin/bash
CURRENT_DIR="$(pwd)"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [[ ! -f "${DIR}/set-env.sh" ]] ; then
  echo "cannot find ${DIR}/set-env.sh file"
  exit -1
fi
source "${DIR}/set-env.sh"

mkdir -p "${DIR}/../.terraform"
set TF_LOG=INFO
set TF_LOG_PATH="${DIR}/../.terraform/plan.sh.log"

cd "${DIR}/.." && terraform init -input=false
cd "${DIR}/.." && terraform plan -input=false

cd "${CURRENT_DIR}"
