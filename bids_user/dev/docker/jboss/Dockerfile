###
#
# jboss-eap:7.4.3 image environment variables
#
# JBOSS_VERSION=7.4
# JBOSS_EAP_PATCH=7.4.3
#
# ADMIN_USER=admin
# ADMIN_PASSWORD=Admin.123
#
# JBOSS_USER=jboss
# JBOSS_USER_HOME=/home/jboss
# JBOSS_HOME=/home/jboss/jboss-eap-7.4
#
###

FROM docker.service.cloud.jeppesensystems.com/crew-buddies/jboss-eap:7.4.3

ARG STANDALONE_ARG='standalone.xml'
ENV STANDALONE=${STANDALONE_ARG} \
    PATH="${PATH}:${JAVA_HOME}/bin"

HEALTHCHECK CMD wget -q --spider http://127.0.0.1:8080/portal/ || exit 1

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["${JBOSS_BIN}/standalone.sh"]

COPY --chown=jboss ./dev/docker/jboss/jboss-eap/modules                                                           ${JBOSS_HOME}/modules
COPY --chown=jboss ./dev/docker/jboss/config                                                                      ${JBOSS_USER_HOME}/config
COPY --chown=jboss ./dev/docker/jboss/config/jeppesen-config/crewweb.properties-default                           ${JBOSS_USER_HOME}/config/jeppesen-config/crewweb.properties
COPY --chown=jboss ./dev/docker/jboss/jboss-eap/standalone/configuration/${STANDALONE}                            ${JBOSS_HOME}/standalone/configuration/standalone.xml
COPY --chown=jboss ./SAS.bid/target/*.war ./SAS.user-directory-import/target/*.war                                ${JBOSS_HOME}/standalone/deployments/
