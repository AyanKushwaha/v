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

set defaultPattern="ib6-sas"
set pattern=%1
if "%pattern%"=="" (
  echo setting default predefined pattern as %defaultPattern%
  set pattern=%defaultPattern%
)

setlocal
setlocal enabledelayedexpansion

call %currentDirPathWithoutSlash%\bin\set-env.cmd
cd %currentDirPathWithoutSlash%\

openstack keypair delete %pattern%-keypair
for /f "usebackq tokens=2 delims=|" %%a in (`openstack server list ^| findstr %pattern%`) do (
  echo run command: openstack server delete %%a
  openstack server delete %%a
)

endlocal

cd %currentDir%
