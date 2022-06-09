#!/usr/bin/env bash
echo '

                  05-dns-fqdn.sh

'

echo 'Register hostname in DNS...'
curl https://git.got.jeppesensystems.com/TD/consul/raw/master/tools/register_service.sh | /bin/bash -s -- "ib6-sas" 20200
