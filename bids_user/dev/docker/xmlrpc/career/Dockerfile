FROM openjdk:8u212-jdk-alpine3.9

ARG PORT_ARG=24056
ARG BACKEND_ARG='ReportServer'
ARG JAR_FILE_ARG='/tmp/xmlrpc-mock-server-all.jar'
ARG CACHE_PATH_ARG='/tmp/report-server-regexp-data'

ENV PORT=${PORT_ARG} \
    BACKEND=${BACKEND_ARG} \
    JAR_FILE=${JAR_FILE_ARG} \
    CACHE_PATH=${CACHE_PATH_ARG}\
    PATH="${PATH}:${JAVA_HOME}/bin" \
    JAVA_OPTS='-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005'

ENTRYPOINT java -jar ${JAR_FILE} -port ${PORT} -backend ${BACKEND} -cachePath ${CACHE_PATH}
CMD /bin/bash
EXPOSE 24056

WORKDIR /tmp
COPY ./dev/xmlrpc-mock-server/data/report-server-regexp-data/manpower/career/            /tmp/report-server-regexp-data/manpower/career/
COPY ./dev/xmlrpc-mock-server/data/report-server-regexp-data/manpower/career/report-server-mappings.properties  /tmp/report-server-regexp-data/
COPY ./dev/xmlrpc-mock-server/data/dispatch-mappings.properties                          /tmp/report-server-regexp-data/
COPY ./dev/xmlrpc-mock-server/target/xmlrpc-mock-server-all.jar                          /tmp/
