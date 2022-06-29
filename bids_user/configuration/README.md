Drop the archive `jboss-eap-6.4.0.zip` from `\\documents\Customer\Implementation\Projects\Bids3PPSoftware\Jboss` to some convenient place and run

    $ ./configure.ps1 -jbossZip path/to/jboss-eap-6.4.0 zip

this will extract the JBoss server into `jboss-eap-6.4` folder and configure the `jboss-eap-6.4/standalone/configuration/standalone.xml`

Or you can extract it by hand and run

    $ ./configure.ps1
