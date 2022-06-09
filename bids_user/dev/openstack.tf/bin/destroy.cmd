@echo off

set currentDir=%cd%

for %%I in (.) do set CurrDirName=%%~nxI
set currentDirPath=%~dp0
set denormalizedBasePath=%currentDirPath:~0,-1%\..
for %%i in ("%denormalizedBasePath%") do SET "currentDirPathWithoutSlash=%%~fi"

if not exist "%currentDirPathWithoutSlash%\bin\set-env.cmd" (
  echo cannot find %currentDirPathWithoutSlash%\bin\set-env.cmd file
  goto :eof
)

call %currentDirPathWithoutSlash%\bin\set-env.cmd
cd %currentDirPathWithoutSlash%\

mkdir .terraform
set TF_LOG=INFO
set TF_LOG_PATH=%currentDirPathWithoutSlash%\.terraform\destroy.cmd.log

terraform destroy -auto-approve -lock=false -force

cd %currentDir%
