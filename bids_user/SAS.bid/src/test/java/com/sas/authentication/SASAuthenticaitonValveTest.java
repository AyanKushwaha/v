package com.sas.authentication;

import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.security.Principal;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpSession;


import org.apache.catalina.Context;
import org.apache.catalina.Realm;
import org.apache.catalina.Session;
import org.apache.catalina.Valve;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.deploy.SecurityConstraint;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;


@RunWith(MockitoJUnitRunner.class)
public class SASAuthenticaitonValveTest {

	AuthenticationValve testee;

	@Mock
	private Request request;
	@Mock
	private Response response;

	@Mock
	private Context context;
	@Mock
	private Realm realm;
	@Mock
	private Valve nextValve;
	@Mock
	private SecurityConstraint securityConstraint;
	@Mock
	private Principal principal;
	@Mock
	private Session session;
	@Mock
	private HttpSession httpSession; 

	private SecurityConstraint[] constraints;
	private String cookieName = "sessId";
	private String sessionId = "12345";
	
	TestAuthenticationConfiguration configuration;

	@Before
	public void setup() throws Exception {
		configuration = new TestAuthenticationConfiguration(cookieName);
		
		testee = new AuthenticationValve(configuration) {
			@Override
			public Valve getNext() {
				return nextValve;
			}
		};
		
		testee.setContainer(context);

		when(context.getRealm()).thenReturn(realm);
		when(context.getPath()).thenReturn("/root");
		when(request.getContextPath()).thenReturn("/root");

		when(request.getSessionInternal(true)).thenReturn(session);
		when(request.getSessionInternal(false)).thenReturn(session);
		
		constraints = new SecurityConstraint[] { securityConstraint };
		when(securityConstraint.getAuthConstraint()).thenReturn(true);
		when(securityConstraint.getAllRoles()).thenReturn(true);
		when(realm.findSecurityConstraints(request, context)).thenReturn(constraints);

		when(realm.hasUserDataPermission(request, response, constraints)).thenReturn(true);
		when(request.getDecodedRequestURI()).thenReturn("/portal");
	}

	
	
	@Test
	public void requestWithoutCookieIsRejected() throws Exception {
		testee.invoke(request, response);

		verifyAuthenticationDidntOccur();
		makeSureNextValveWasNotInvoked();
	}
	

	@Test
	public void requestWithCookiesIsPassedOnToRealmForAuthentication() throws Exception {
		Cookie cookie = new Cookie(cookieName, sessionId);
		when(request.getCookies()).thenReturn(new Cookie[] { cookie });
		given(realm.authenticate(sessionId, configuration.getDummyPassword())).willReturn(principal);
		given(realm.hasResourcePermission(request, response, constraints, this.context)).willReturn(true);
		
		testee.invoke(request, response);

		verify(realm).authenticate(sessionId, configuration.getDummyPassword());
		makeSureNextValveWasInvoked();
	}
	
	@Test
	public void anAlreadyAuthenticatedRequestWithStillVaidSSOSessionisSimplyPassedOn() throws Exception {
		Cookie cookie = new Cookie(cookieName, sessionId);
		when(request.getCookies()).thenReturn(new Cookie[] { cookie });
		
		given(request.getUserPrincipal()).willReturn(principal);
		given(realm.hasResourcePermission(request, response, constraints, this.context)).willReturn(true);

		testee.invoke(request, response);

		verifyAuthenticationDidntOccur();
		makeSureNextValveWasInvoked();
	}


	@Test
	public void anAlreadyAuthenticatedRequestIsReLoggedInWhenSSOSessionChanged() throws Exception {

		Cookie cookie = new Cookie(cookieName, sessionId);
		when(request.getCookies()).thenReturn(new Cookie[] { cookie });

		when(session.getPrincipal()).thenReturn(principal);
		when(principal.getName()).thenReturn("nonAuthenticatedUserId");
		
		when(request.getSession()).thenReturn(httpSession);
		given(realm.hasResourcePermission(request, response, constraints, this.context)).willReturn(true);
		
		testee.invoke(request, response);

		// Make sure a proper logout was called and that the request was re-directed to the portal
		verify(session).setPrincipal(null);
		verify(httpSession).invalidate();
		verifyAuthenticationDidntOccur();
		verify(response).sendRedirect(request.getContextPath() + "/portal");
		makeSureNextValveWasNotInvoked(); // we are redirecting the user to login page
	}
	

	
	private void verifyAuthenticationDidntOccur() {
		verify(realm, never()).authenticate(sessionId, sessionId);
	}

	private void makeSureNextValveWasInvoked() throws Exception {
		verify(response).setHeader("Pragma", "No-cache");
		verify(response).setHeader("Cache-Control", "no-cache");
		verify(nextValve).invoke(request, response);
	}
	
	private void makeSureNextValveWasNotInvoked() throws Exception {
		verify(nextValve, never()).invoke(request, response);
	}


	
}
