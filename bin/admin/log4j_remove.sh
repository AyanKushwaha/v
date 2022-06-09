
 for pathToJar in ` find /usr/java/jboss-eap-6.4 -name "log4j-core*.jar" | xargs grep JndiLookup.class  | awk '{print $3}' `; do zip -q -d $pathToJar org/apache/logging/log4j/core/lookup/JndiLookup.class "\n\n\n";done;
  for pathToJar in ` find /opt/Carmen/CARMUSR/ -name "log4j-core*.jar" | xargs grep JndiLookup.class  | awk '{print $3}' `; do zip -q -d $pathToJar org/apache/logging/log4j/core/lookup/JndiLookup.class "\n\n\n";done;
