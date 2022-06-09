###
#
# jboss-eap:6.4.19 image environment variables
#
# JBOSS_VERSION=6.4
# JBOSS_EAP_PATCH=6.4.19
#
# ADMIN_USER=admin
# ADMIN_PASSWORD=Admin.123
#
# JBOSS_USER=jboss
# JBOSS_USER_HOME=/home/jboss
# JBOSS_HOME=/home/jboss/jboss-eap-6.4
#
###

FROM docker.service.cloud.jeppesensystems.com/crew-buddies/jboss-eap:6.4.22

ARG STANDALONE_ARG='standalone.xml'
ENV STANDALONE=${STANDALONE_ARG} \
    PATH="${PATH}:${JAVA_HOME}/bin" \
    JAVA_OPTS="$JAVA_OPTS -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005"

EXPOSE 5005

HEALTHCHECK CMD wget -q --spider http://127.0.0.1:8080/portal/ || exit 1

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["${JBOSS_BIN}/standalone.sh"]

COPY --chown=jboss ./dev/docker/jboss/jboss-eap-6.4/modules                                                       ${JBOSS_HOME}/modules
COPY --chown=jboss ./dev/docker/jboss/config                                                                      ${JBOSS_USER_HOME}/config
COPY --chown=jboss ./dev/docker/jboss/config/jeppesen-config/crewweb.properties-default                           ${JBOSS_USER_HOME}/config/jeppesen-config/crewweb.properties
COPY --chown=jboss ./dev/docker/jboss/jboss-eap-6.4/standalone/configuration/${STANDALONE}                        ${JBOSS_HOME}/standalone/configuration/standalone.xml
COPY --chown=jboss ./SAS.bid/target/*.war ./SAS.user-directory-import/target/*.war                                ${JBOSS_HOME}/standalone/deployments/
