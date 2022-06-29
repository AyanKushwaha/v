package com.sas.authentication;

import com.jeppesen.jcms.crewweb.common.util.CWLog;

import javax.security.jacc.PolicyContext;
import javax.security.jacc.PolicyContextException;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;

public class AuthenticationUtil {

	private final CWLog log = CWLog.getLogger(AuthenticationUtil.class);

	public boolean requestHasSSOCookie(HttpServletRequest request, String cookieName) {
		Cookie[] cookies = request.getCookies();
		if (cookies != null) {
			for (Cookie c : cookies) {
				if (cookieName.equals(
						c.getName())) {
					return true;
				}
			}
		}
		return false;
	}

	public String getSessionIdFromMagicCookie(HttpServletRequest request, String cookieName) {
		Cookie[] cookies = request.getCookies();
		return getCookieValue(cookies, cookieName);
	}

	public String getCookieValue(Cookie[] cookies, String cookieName) {
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

	public HttpServletRequest getHttpRequest() {
		try {
			return (HttpServletRequest) PolicyContext.getContext(HttpServletRequest.class.getName());
		} catch (PolicyContextException e) {
			throw new RuntimeException("Failed to fetch the Http Request from LoginModule.", e);
		}
	}
}
