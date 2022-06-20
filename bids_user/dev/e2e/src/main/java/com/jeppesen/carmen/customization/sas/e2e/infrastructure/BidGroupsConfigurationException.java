package com.jeppesen.carmen.customization.sas.e2e.infrastructure;

public class BidGroupsConfigurationException extends RuntimeException {
    public BidGroupsConfigurationException() {
        super(
                "Please, check you application.properties file!" +
                        " Configuration crewportal.bidGroups should" +
                        " contains bid group list values. Example:" +
                        " crewportal.bidGroups=GR1,GR2,GR3"
        );
    }
}
