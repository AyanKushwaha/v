package com.sas.authentication;

import javax.security.jacc.PolicyContextException;
import javax.servlet.http.HttpServletRequest;

import org.apache.catalina.connector.Request;
import org.jboss.security.auth.spi.DatabaseServerLoginModule;

public class LoginModuleWithRolesInDatabase extends DatabaseServerLoginModule {

	private SASAuthenticationConfiguration configuration;

	public LoginModuleWithRolesInDatabase() throws Exception {
		this(new DefaultSASAuthenticationConfiguration());
	}

	public LoginModuleWithRolesInDatabase(
			SASAuthenticationConfiguration configuration) {
		super();
		this.configuration = configuration;
	}

	@Override
	protected boolean validatePassword(String inputPassword, String expectedPassword) {

		HttpServletRequest request;

		boolean validated = false;

		try {
			request = (HttpServletRequest) javax.security.jacc.PolicyContext
					.getContext(HttpServletRequest.class.getName());
			if (isValidEmptyPasswordLogin()) {
				validated = true;
			} else if (isValidSSOCookieLoginWithoutExpectedPassword((Request) request, expectedPassword)) {
				validated = true;
			} else if (isValidPasswordLogin(inputPassword, expectedPassword)) {
				validated = true;
			}
		} catch (PolicyContextException e) {
		}

		return validated;
	}

	private boolean isValidEmptyPasswordLogin() {
		return configuration.allowEmptyPaswordLogin();
	}

	private boolean isValidSSOCookieLoginWithoutExpectedPassword(
			Request request, String expectedPassword) {

		return (AuthenticationUtil.requestHasSSOCookie((Request) request,
				configuration.getAuthenticationCookieName()) && !(expectedPassword != null && !expectedPassword
				.isEmpty()));
	}

	private boolean isValidPasswordLogin(String inputPassword,
			String expectedPassword) {
		return (inputPassword != null && !inputPassword.isEmpty()
				&& expectedPassword != null && !expectedPassword.isEmpty() && inputPassword
					.equals(expectedPassword));
	}
}
