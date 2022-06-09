package com.jeppesen.jcms.customization.sas.parsing;

import java.util.Arrays;

import com.jeppesen.jcms.customization.template.parsing.UserData;
import com.jeppesen.jcms.customization.template.processing.OldRolesToCacsRolesMapper;

public class SASRoleMapper implements OldRolesToCacsRolesMapper {

	@Override
	public Iterable<String> getCacsRolesForUser(UserData user) {

		CharSequence adminRole = "admin";
		for (String role : user.getRoles()) {
			if (role.toLowerCase().contains(adminRole)) {
				return Arrays.asList("administrator");
			}
		}
		
		return Arrays.asList("crew");
	}
}