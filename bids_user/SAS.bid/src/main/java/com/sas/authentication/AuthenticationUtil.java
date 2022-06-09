package com.sas.authentication;

import javax.servlet.http.Cookie;

import org.apache.catalina.connector.Request;

public class AuthenticationUtil {

	public static boolean requestHasSSOCookie(Request request, String cookieName) {
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

}
