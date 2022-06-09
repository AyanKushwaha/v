@echo off

rem OpenStack will be using these env variables:
set OS_USER_DOMAIN_ID=
set OS_USER_DOMAIN_NAME=Default
set OS_PROJECT_DOMAIN_ID=default
set OS_PROJECT_NAME=crewbuddies
set OS_USERNAME=crewbuddies
set OS_PASSWORD=jeppesen_crewbuddies
set OS_IDENTITY_API_VERSION=3
set OS_AUTH_URL=https://gotosp13.osp.jeppesensystems.com:13000/v3/

rem Transfer same OpenStack env variables for reuse into Terraform:
set TF_VAR_domain_name=%OS_USER_DOMAIN_NAME%
set TF_VAR_os_tenant_name=%OS_PROJECT_NAME%
set TF_VAR_os_username=%OS_USERNAME%
set TF_VAR_os_password=%OS_PASSWORD%
set TF_VAR_auth_url=%OS_AUTH_URL%
