package com.sas.authentication;

public interface SASAuthenticationConfiguration {

	String COOKIE_NAME = "java:global/jcms/customization/sas/portal-appl-sessID-param";
	String ALLOW_FORM_BASED_LOGIN = "java:global/jcms/customization/sas/allow-form-based-login";
	String ALLOW_EMPTY_PASSWORD = "java:global/jcms/customization/sas/allow-empty-password";

	String getAuthenticationCookieName();

	boolean allowFormBasedLogin();
	
	boolean allowEmptyPaswordLogin();

	/**
	 * This is a dummy password used for jboss authentication of a sso request. The authentication realm, .i.e. the configured login modules, 
	 * do not care about the password for a sso authenticated request.
	 */
	String getDummyPassword();
}
