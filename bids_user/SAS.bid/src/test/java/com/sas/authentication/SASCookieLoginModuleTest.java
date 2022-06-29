package com.sas.authentication;

import org.apache.catalina.connector.Request;
import org.junit.jupiter.api.*;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import javax.security.auth.login.LoginException;
import javax.servlet.http.Cookie;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.MockitoAnnotations.initMocks;

@DisplayName("SASCookieLoginModule tests")
@DisplayNameGeneration(DisplayNameGenerator.ReplaceUnderscores.class)
public class SASCookieLoginModuleTest {

    @InjectMocks
    private SASCookieLoginModule testee;

    @Mock
    private Request request;
    @Mock
    private AuthenticationUtil authenticationUtil;
    @Mock
    private DefaultSASAuthenticationConfiguration configuration;

    private final String cookieName = "sessId";
    private final String sessionId = "12345";
    private final Cookie cookie = new Cookie(cookieName, sessionId);
    private final Cookie[] cookies = new Cookie[] { cookie };

    @BeforeEach
    public void setUp() {
        initMocks(this);
    }

    @Test
    public void should_fail_if_request_has_no_sso_cookie() throws LoginException {
        givenDefaultConfiguration();
        given(authenticationUtil.getSessionIdFromMagicCookie(request, cookieName)).willReturn(null);

        boolean result = testee.login();

        verify(authenticationUtil, times(2));
        assertFalse(result);
    }

    private void givenDefaultConfiguration() {
        given(request.getCookies()).willReturn(cookies);
        given(configuration.getAuthenticationCookieName()).willReturn(cookieName);
        given(authenticationUtil.getHttpRequest()).willReturn(request);
    }
}
