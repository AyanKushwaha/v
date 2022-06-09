if EXIST "C:\Users\%USERNAME%\AppData\LocalLow\Sun\Java\Deployment\LoggingStatus.txt" GOTO Done
ECHO %Date%,%Time% >"C:\Users\%USERNAME%\AppData\LocalLow\Sun\Java\Deployment\LoggingStatus.txt"
ECHO deployment.trace.level=basic >>"C:\Users\%USERNAME%\AppData\LocalLow\Sun\Java\Deployment\deployment.properties"
ECHO deployment.trace=true >>"C:\Users\%USERNAME%\AppData\LocalLow\Sun\Java\Deployment\deployment.properties"
ECHO deployment.user.logdir=c\:\\CMS2logs\\%USERNAME%\\ >>"C:\Users\%USERNAME%\AppData\LocalLow\Sun\Java\Deployment\deployment.properties"
:Done