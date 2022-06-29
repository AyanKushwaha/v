SAS.deploy

This artifact is used by the cmsshell "crewportal deploy" script.
It uses the configuration defined in $CARMUSR/etc/subsystems/bids/<CARMSYSTEMNAME>.xml to determine where to copy application configuration files and where to deploy the artifacts (SAS.bid, SAS.user-directory-import).
The deployment artifacts should be copied to the jboss deployments folder.