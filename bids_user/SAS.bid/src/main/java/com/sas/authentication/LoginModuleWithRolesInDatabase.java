package com.sas.authentication;

import org.jboss.security.auth.spi.DatabaseServerLoginModule;

import javax.servlet.http.HttpServletRequest;

import static org.apache.commons.lang.StringUtils.isEmpty;
import static org.apache.commons.lang.StringUtils.isNotEmpty;

public class LoginModuleWithRolesInDatabase extends DatabaseServerLoginModule {

    private final SASAuthenticationConfiguration configuration;
    private final AuthenticationUtil authenticationUtil;

    public LoginModuleWithRolesInDatabase() throws Exception {
        this(new DefaultSASAuthenticationConfiguration());
    }

    public LoginModuleWithRolesInDatabase(SASAuthenticationConfiguration configuration) {
        this(configuration, new AuthenticationUtil());
    }

    public LoginModuleWithRolesInDatabase(SASAuthenticationConfiguration configuration,
                                          AuthenticationUtil authenticationUtil) {
        this.configuration = configuration;
        this.authenticationUtil = authenticationUtil;
    }

    @Override
    protected boolean validatePassword(String inputPassword, String expectedPassword) {
        HttpServletRequest request;
        request = authenticationUtil.getHttpRequest();

        return (isValidEmptyPasswordLogin()) ||
                (isValidSSOCookieLoginWithoutExpectedPassword(request, expectedPassword)) ||
                (isValidPasswordLogin(inputPassword, expectedPassword));
    }

    private boolean isValidEmptyPasswordLogin() {
        return configuration.allowEmptyPaswordLogin();
    }

    private boolean isValidSSOCookieLoginWithoutExpectedPassword(HttpServletRequest request, String expectedPassword) {
        return authenticationUtil.requestHasSSOCookie(request, configuration.getAuthenticationCookieName())
                && isEmpty(expectedPassword);
    }

    private boolean isValidPasswordLogin(String inputPassword, String expectedPassword) {
        return isNotEmpty(inputPassword)
                && isNotEmpty(expectedPassword)
                && inputPassword.equals(expectedPassword);
    }
}
