package com.sas.authentication;

import javax.naming.InitialContext;
import javax.naming.NamingException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSASAuthenticationConfiguration implements SASAuthenticationConfiguration {

	private static final Logger LOG = LoggerFactory.getLogger(DefaultSASAuthenticationConfiguration.class);
	private String authenticationCookieName;
	private final String dummyValue = "}3hz_18#||6Eq8r";
	private boolean allowFormBasedLogin;
	private boolean allowEmptyPassword;

	public DefaultSASAuthenticationConfiguration() throws NamingException, Exception {
		this(new InitialContext());
	}

	public DefaultSASAuthenticationConfiguration(InitialContext initialContext) {
		initialize(initialContext);
	}

	void initialize(InitialContext context) {
		try {
			authenticationCookieName = (String) context.lookup(SASAuthenticationConfiguration.COOKIE_NAME);
			allowFormBasedLogin = getJNDILookupWithDefaultValue(context, ALLOW_FORM_BASED_LOGIN, false);
			allowEmptyPassword = getJNDILookupWithDefaultValue(context, ALLOW_EMPTY_PASSWORD, false);

		} catch (Exception e) {
			throw new RuntimeException("Incorrect configuration ==============> Bids will not start or function properly", e);
		}
	}
	
	private boolean getJNDILookupWithDefaultValue(InitialContext context, String jndiName, boolean defaultValue) {
		try {
			return Boolean.parseBoolean((String) context.lookup(jndiName));
		} catch (Exception e) {
			LOG.info("JNDI name " + jndiName + " not set, using default value \"" + defaultValue + "\"");
			return defaultValue;
		}
	}

	@Override
	public String getAuthenticationCookieName() {
		return authenticationCookieName;
	}

	@Override
	public String getDummyPassword() {
		return dummyValue;
	}

	@Override
	public boolean allowFormBasedLogin() {
		return allowFormBasedLogin;
	}
	
	@Override
	public boolean allowEmptyPaswordLogin() {
		return allowEmptyPassword;
	}
}
