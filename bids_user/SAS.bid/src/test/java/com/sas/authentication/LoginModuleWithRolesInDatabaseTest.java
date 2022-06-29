package com.sas.authentication;

import org.apache.catalina.connector.Request;
import org.junit.jupiter.api.*;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import javax.security.auth.login.LoginException;
import javax.servlet.http.Cookie;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.BDDMockito.given;
import static org.mockito.MockitoAnnotations.initMocks;

@DisplayName("LoginModuleWithRolesInDatabase tests")
@DisplayNameGeneration(DisplayNameGenerator.ReplaceUnderscores.class)
public class LoginModuleWithRolesInDatabaseTest {

    @InjectMocks
    private LoginModuleWithRolesInDatabase testee;

    @Mock
    private Request request;
    @Mock
    private AuthenticationUtil authenticationUtil;
    @Mock
    private DefaultSASAuthenticationConfiguration configuration;

    private final String password = "abc";
    private final String cookieName = "sessId";
    private final String sessionId = "12345";
    private final Cookie cookie = new Cookie(cookieName, sessionId);
    private final Cookie[] cookies = new Cookie[] { cookie };

    @BeforeEach
    public void setUp() {
        initMocks(this);
    }

    @Test
    public void should_pass_if_empty_password_allowed() throws LoginException {
        givenDefaultConfiguration();
        given(configuration.allowEmptyPaswordLogin()).willReturn(true);

        boolean result = testee.validatePassword(password, "");

        assertTrue(result);
    }

    @Test
    public void should_pass_with_sso_cookie_present_in_request_and_no_password() throws LoginException {
        givenDefaultConfiguration();
        given(authenticationUtil.requestHasSSOCookie(request, cookieName)).willReturn(true);

        boolean result = testee.validatePassword(password, null);

        assertTrue(result);
    }

    @Test
    public void should_pass_if_password_match() throws LoginException {
        givenDefaultConfiguration();

        boolean result = testee.validatePassword(password, password);

        assertTrue(result);
    }

    @Test
    public void should_fail_if_password_do_not_match() throws LoginException {
        givenDefaultConfiguration();

        boolean result = testee.validatePassword(password, "wrong_password");

        assertFalse(result);
    }

    @Test
    public void should_fail_if_sso_cookie_present_in_request_and_any_password() throws LoginException {
        givenDefaultConfiguration();
        given(authenticationUtil.requestHasSSOCookie(request, cookieName)).willReturn(true);

        boolean result = testee.validatePassword(password, "any_password");

        assertFalse(result);
    }

    private void givenDefaultConfiguration() {
        given(request.getCookies()).willReturn(cookies);
        given(configuration.getAuthenticationCookieName()).willReturn(cookieName);
        given(authenticationUtil.getHttpRequest()).willReturn(request);
        given(configuration.allowEmptyPaswordLogin()).willReturn(false);
        given(authenticationUtil.requestHasSSOCookie(request, cookieName)).willReturn(false);
    }
}
