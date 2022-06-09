package com.jeppesen.jcms.customization.template.parsing;

import java.util.ArrayList;
import java.util.List;

public class UserData {

	private String loginId;
	private String userId;
	private String firstName;
	private String lastName;
	private String password;
	private boolean inactive;
	private List<String> roles;

	@Override
	public String toString() {
		return String.format("UserData [login=%s,u=%s, p=%s, f=%s,l=%s,i=%s]", loginId, userId, password, firstName, lastName, inactive);
	}

	public String getUserId() {
		return userId;
	}

	public void setUserId(String userId) {
		this.userId = userId;
	}

	public String getLoginId() {
		return loginId;
	}

	public void setLoginId(String loginId) {
		this.loginId = loginId;
	}

	public String getFirstName() {
		return firstName;
	}

	public void setFirstName(String surname) {
		this.firstName = surname;
	}

	public String getLastName() {
		return lastName;
	}

	public void setLastName(String lastName) {
		this.lastName = lastName;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}
	
	public void setInactive(boolean inactive) {
		this.inactive = inactive;
	}

	public boolean isInactive() {
		return this.inactive;
	}

	public List<String> getRoles() {
		return roles;
	}

	public void setRoles(List<String> roles) {
		this.roles = roles;
	}

	public void addRole(String roleName) {
		if (roles == null) {
			roles = new ArrayList<String>();
		}
		roles.add(roleName);
	}

}