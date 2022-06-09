#!/bin/bash
TARGET_DIR="../cms_accounts"
REPO="git@ssh.dev.azure.com:v3/flysas/SAS-CMS/cms_accounts"

if [ -e "${TARGET_DIR}" ]
then
    pushd $TARGET_DIR
    git pull --rebase
    popd
else
    # Need to quieten git clone output, since it writes to stderr for some stupid reason
    git clone --quiet $REPO $TARGET_DIR
fi