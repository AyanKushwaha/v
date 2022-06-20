# E2E solution

## Build, test and run

### Usage

_execute e2e tests locally (without Selenium Hub)_

mvnw -f .\dev\docker -P up

mvnw -f .\dev\e2e -P local
mvnw -f .\dev\e2e -P chrome
mvnw -f .\dev\e2e -P firefox

mvnw -f .\dev\docker -P down
```

_execute e2e tests with Selenium Hub on windows_

mvnw -f .\dev\docker -P e2e-up

mvnw -f .\dev\e2e -P remote
mvnw -f .\dev\e2e -P remote-firefox
mvnw -f .\dev\e2e -P remote-chrome

mvnw -f .\dev\docker -P e2e-down
```

### System settings with maven

To set needed system setting for test execution,
use `-DargLine="...""` approach:

```cmd
mvnw -f e2e test -DargLine="-Dbrowser=firefox -Dremote=http://127.0.0.1:4444/wd/hub -Dcrewportal.server.jBossHost=jboss"
```

### Filter tests to be executed

Fot customers more valuable only E2E tests, not internal
framework functionality we are using to write them, so
we can reduce testing time by executing only interested
features and user-stories, without not necessary
overhead

_run only e2e tests_

```bash
./mvnw -f ./dev/e2e -P remote-chrome -Dgroups=E2E
```

NOTE: this will run tests only marked with `@Tag("E2E)`
      annotation, so if total e2e test time is very
      high, we can reduce it by using this approach

_run only page object tests_

```bash
./mvnw -f ./dev/e2e -P remote-chrome -Dgroups=PO
```

_we can also ask maven execute few tags_

```bash
./mvnw -f ./dev/e2e -P remote-chrome -Dgroups=PO,E2E
```

this will wun both: PO and E2E tagged tests

### Selenium Hub

open http://127.0.0.1:4444/grid/console/
to see Selenium Hub cluster nodes registered

<!--

## RoadMap 

### Currently in progress

* `Selenium` -> `Selenide` migration to reduce complexity and it's
  verbosity. We can use all good stuff available in Selenide
  library to make testing or new features cover useful, simple and
  effective (ask me to show it if you are interesting...)
* Make e2e testing solution __more portable__ to other
  customizations or at least to spend less time for each new
  customization testing introduction. Build _more_ framework 
  _reusable_ abstractions, components (business focused page
  objects, not just a webdriver page objects as people is often
  doing) and extensible _configurations_ per customization
* Main cons of any E2E testing is it's high complexity and low
  execution speed, which is usually in result cost a lot of money
  for business, but CrewBuddies currently working on minimization
  each of these factors (ask me to show a simple demo to compare)

### Missing / partially missing parts (required to be done)

* Implement DB Fixtures by using JPA or R2DBC for test data
  preparation. This is needed not only in scope of E2E testing
  solution, but also for generic CrewPortal development use.
  _Some part of this_ implementation and other useful background
  _was already processed by us_ during GDPR implementation
* Prepare quick transfer knowledge for team how to quickly and 
  effective test exact we need without overheat + some best
  practices from my personal experience I've got during e2e
  implementation

### Other / optional things (depends on customers needs)

* Cover about _25% of Test Plan_ existing user stories. This should
  give us a filling after each success build got a chance to test
  about 80% possible issues: ~20% administration page mostly wont
  be covered except period creation and flush cache, other part is
  _bidding_ basic _business logic + CRUD_ operations for _JBoss
  Security latest patching upgrade_ activities
* Find some time to tune, configure and setup gitlab runner on our
  mac mini. Prepare and test if it's possible to run GitLab runners
  automation tests for Safari browser, similar to like we are doing
  on out linux runners and UI tests
* Talk to Atlas team and ask them for some help with Windows
  OpenStack visualization automation: Setup windows machine with
  proper IE / Edge browsers installed if some customers require any
  of them. Also install GitLab runner for windows platform similar
  to previous step

-->

## Update versions

_assuming you have in your `pom.xml` file next plugin config:_

```xml
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>versions-maven-plugin</artifactId>
        <version>2.7</version>
        <configuration>
          <generateBackupPoms>false</generateBackupPoms>
          <allowSnapshots>true</allowSnapshots>
          <allowIncrementalUpdates>true</allowIncrementalUpdates>
          <excludeReactor>false</excludeReactor>
        </configuration>
      </plugin>
```

_check for new versions with command:_

```batch
mvnw -f .\dev\e2e\pom.xml versions:display-dependency-updates

mvnw -f .\dev\e2e\pom.xml versions:display-parent-updates
mvnw -f .\dev\e2e\pom.xml versions:display-plugin-updates
mvnw -f .\dev\e2e\pom.xml versions:display-property-updates
```

see reference for [dependencies](https://www.mojohaus.org/versions-maven-plugin/examples/display-dependency-updates.html) versions updates
and reference for [plugins](https://www.mojohaus.org/versions-maven-plugin/examples/display-plugin-updates.html) versions updates

## Resources

- [Github: daggerok/jboss-docker-e2e-solution](https://github.com/daggerok/jboss-docker-e2e-solution)
- [Github: daggerok/e2e-starter](https://github.com/daggerok/e2e-starter)
- [Pass java system properties with maven](https://maven.apache.org/surefire/maven-surefire-plugin/examples/system-properties.html)
- [Fluent way to wait Selenium element correctly](https://developers.perfectomobile.com/display/TT/Selenium+Waits)
- [ExpectedConditions usage](https://www.testingexcellence.com/webdriver-explicit-implicit-fluent-wait/)
- [Getting Started Selenium Hub](https://github.com/SeleniumHQ/docker-selenium/wiki/Getting-Started-with-Hub-and-Nodes)
- [Selenide](https://selenide.org/documentation/selenide-vs-selenium.html)
