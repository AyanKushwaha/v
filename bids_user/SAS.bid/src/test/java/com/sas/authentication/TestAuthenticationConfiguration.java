package com.sas.authentication;

public class TestAuthenticationConfiguration implements SASAuthenticationConfiguration {

	private String cookieName;
	
	private final String anyPassword = "dummy-password";

	public TestAuthenticationConfiguration(String cookieName) {
		this.cookieName = cookieName;
	}

	@Override
	public String getAuthenticationCookieName() {
		return cookieName;
	}

	@Override
	public boolean allowFormBasedLogin() {
		return false;
	}

	@Override
	public boolean allowEmptyPaswordLogin() {
		return false;
	}

	@Override
	public String getDummyPassword() {
		return anyPassword;
	}

}
