# Customer specific JBoss

Whole JBoss folder is ignored except developer-specific configurations.

1. Download JBoss EAP 6.4
2. Unzip and place all content inside jboss-eap-6.4 folder (do not replace existed files)
3. copy each *-default file and reconfigure it (search for 'CHANGE ME' in workspace)
   - jboss-files/resources/crewweb.properties-default -> jboss-files/resources/crewweb.properties
   - jboss-eap-6.4/standalone/configuration/standalone.xml-default -> jboss-eap-6.4/standalone/configuration/standalone.xml
