package com.sas.authentication;

import org.apache.catalina.connector.Request;
import org.junit.jupiter.api.*;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import javax.servlet.http.Cookie;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.BDDMockito.given;
import static org.mockito.MockitoAnnotations.initMocks;

@DisplayName("AuthenticationUtil tests")
@DisplayNameGeneration(DisplayNameGenerator.ReplaceUnderscores.class)
public class AuthenticationUtilTest {

    @InjectMocks
    private AuthenticationUtil testee;

    @Mock
    private Request request;

    private final String cookieName = "sessId";
    private final String sessionId = "12345";
    private final Cookie cookie = new Cookie(cookieName, sessionId);
    private final Cookie[] cookies = new Cookie[] { cookie };

    @BeforeEach
    public void setUp() {
        initMocks(this);
    }

    @Test
    public void should_pass_if_request_has_sso_cookie() {
        givenDefaultConfiguration();

        boolean result = testee.requestHasSSOCookie(request, cookieName);

        assertTrue(result);
    }

    @Test
    public void should_find_sso_cookie_successfully() {
        givenDefaultConfiguration();

        String result = testee.getCookieValue(cookies, cookieName);

        assertEquals(sessionId, result);
    }

    private void givenDefaultConfiguration() {
        given(request.getCookies()).willReturn(cookies);
    }
}
