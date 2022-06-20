package com.jeppesen.carmen.customization.sas.e2e.infrastructure;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import org.springframework.validation.annotation.Validated;

import javax.validation.constraints.NotNull;
import java.util.List;

@Data
@Component
@Validated
@ConfigurationProperties(prefix = "crewportal")
public class CrewPortalProps {

    private Server server;
    private Login login;
    private Tabs tabs;
    private AdministrationPage administrationPage;
    private BiddingPage biddingPage;

    @Data
    public static class Server {
        private String jBossHost;
        private String baseUrl;
        private String uri;
        private DB db;

        @Data
        public static class DB {
            private String username;
            private String password;
        }
    }

    @Data
    public static class Login {
        private Admin admin;
        private Crew crew;

        @Data
        public static class Admin {
            private String username;
            private String password;
        }

        @Data
        public static class Crew {
            private String username;
            private String password;
            private String fullName;
        }
    }

    @Data
    public static class Tabs {
        private String administration;
        private String interbids;
        private String vacation;
        private String fda;
    }

    @Data
    public static class AdministrationPage {

        private String periodType;

        @NotNull
        private List<String> groups;

        @NotNull
        private List<String> serverModules;

        private String periodStartDate;
    }

    @Data
    public static class BiddingPage {

        private String visaUs;

        @NotNull
        private List<String> bidCategories;

        @NotNull
        private Integer maxBidsCount;
    }
}
