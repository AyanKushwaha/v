package com.sas.authentication;

import java.io.IOException;
import java.security.Principal;

import javax.servlet.ServletException;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletResponse;

import org.apache.catalina.Realm;
import org.apache.catalina.Session;
import org.apache.catalina.authenticator.AuthenticatorBase;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.deploy.LoginConfig;
import org.apache.catalina.deploy.SecurityConstraint;
import org.jboss.logging.Logger;

/**
 * Authentication is either handled using the unrestricted (anonymous unauthorized access is allowed) Ajax/JAX-RS portal service, OR this
 * filter picks up magic cookies or request parameters which may be valid and correspond to a user that we can identify.
 * <p>
 * This filter overrides the {@link #invoke(Request, Response)} method of it's parent in order to look for magic parameters. If they are
 * found, a normal {@link #login(Request, String, String)} is attempted.
 * <p>
 * The parent's {@link #invoke(Request, Response)} method is then called, allowing the default processing of requests. As such, this filter
 * should be non-intrusive while still guard protected resources according to the security-constraints setup for the web application.
 */
/*
 * For more information, see (long URLs, concatenate manually): 
 * https://access.redhat.com/site/documentation/en-US/JBoss_Enterprise_Application_Platform /6.1/html/Development_Guide/
 * .../Use_A_Third-Party_Authentication_System_In_Your_Application.html 
 * .../About_Authenticator_Valves.html
 * .../Configure_a_Web_Application_to_use_a_Valve.html .../Configure_a_Web_Application_to_use_an_Authenticator_Valve.html
 */
public class AuthenticationValve extends AuthenticatorBase {

	private final Logger log = Logger.getLogger(AuthenticationValve.class);
	private final SASAuthenticationConfiguration configuration;

	public AuthenticationValve() throws Exception{
		this(new DefaultSASAuthenticationConfiguration());
	}
	
	public AuthenticationValve(SASAuthenticationConfiguration configuration) {
		this.configuration = configuration;
	}

	/**
	 * Setting up a principal is either done by the portal's Ajax service, or is setup by this filter's call to
	 * {@link #login(Request, String, String)} from {@link #invoke(Request, Response)}.
	 */
	@Override
	protected boolean authenticate(Request request, HttpServletResponse response, LoginConfig loginConfig) throws IOException {
		if (request.getPrincipal() == null) {
			
			if (AuthenticationUtil.requestHasSSOCookie(request, configuration.getAuthenticationCookieName())) {
				return true;
			}
			
			response.sendRedirect(request.getContextPath());
			return false;
		}
		return true;
	}

	/**
	 * We override this method to check for third party provided authentication tokens, also known as perimeter security.
	 */
	@Override
	public void invoke(Request request, Response response) throws IOException, ServletException {
		if (log.isDebugEnabled()) {
			log.debug("Security checking request " + request.getMethod() + " " + request.getRequestURI());
		}

		if (requestUriIsntSubjectToSecurityContraint(request, response)) {
			getNext().invoke(request, response);
			return;

		} else if (AuthenticationUtil.requestHasSSOCookie(request, configuration.getAuthenticationCookieName())) {

			if (!thereIsACachedAuthenticatedPrincipal(request)) {
				String loginId = getSessionIdFromMagicCookie(request);
				login(request, loginId, configuration.getDummyPassword());
			} else {
				// force a re-login of user if the sso cookie user differs from 
				//  the logged in/authenticated user.
				if (!isAuthencticatedUserAndSSOCookieUserTheSame(request)) {
					logout(request);
					request.getSession().invalidate();
					response.sendRedirect(request.getContextPath() + "/portal");
					return;
				}
			}
		}

		super.invoke(request, response);
	}

	private boolean isAuthencticatedUserAndSSOCookieUserTheSame(Request request) {

		boolean authenticated = true;

		Session session = request.getSessionInternal(true);
		if (session != null) {
			Principal principal = session.getPrincipal();

			if (principal != null) {
				String ssoUserId = getSessionIdFromMagicCookie(request);
				authenticated = principal.getName().equals(ssoUserId);
			}
		}

		return authenticated;
	}

	private boolean requestUriIsntSubjectToSecurityContraint(Request request, Response response) throws IOException, ServletException {
		Realm realm = this.context.getRealm();
		SecurityConstraint[] constraints = realm.findSecurityConstraints(request, this.context);

		// Is this request URI subject to a security constraint?
		if ((constraints == null) /* && (!Constants.FORM_METHOD.equals(config.getAuthMethod())) */) {
			if (log.isDebugEnabled())
				log.debug(" Not subject to any constraint");
			return true;
		}
		return false;
	}

	private boolean thereIsACachedAuthenticatedPrincipal(Request request) {
		// Have we got a cached authenticated Principal to record?
		if (cache) {
			Principal principal = request.getUserPrincipal();
			if (principal == null) {
				Session session = request.getSessionInternal(true);
				if (session != null) {
					principal = session.getPrincipal();
					if (principal != null) {
						if (log.isDebugEnabled()) {
							log.debug("We have cached auth type " + session.getAuthType() + " for principal " + session.getPrincipal());
						}
						return true;
					}
				}
			}
		}
		return false;
	}

	private String getSessionIdFromMagicCookie(Request request) {
		Cookie[] cookies = request.getCookies();
		String authenticationCookieName = configuration.getAuthenticationCookieName();
		return getCookieValue(cookies, authenticationCookieName);
	}

	private String getCookieValue(Cookie[] cookies, String cookieName) {
		if (cookies != null) {
			for (Cookie cookie : cookies) {
				log.trace("Matching cookieToken:" + cookieName + " with cookie name=" + cookie.getName());
				if (cookieName.equals(cookie.getName())) {
					if (log.isTraceEnabled()) {
						log.trace("Cookie-" + cookieName + " value=" + cookie.getValue());
					}
					return cookie.getValue();
				}
			}
		}
		return null;
	}

}
