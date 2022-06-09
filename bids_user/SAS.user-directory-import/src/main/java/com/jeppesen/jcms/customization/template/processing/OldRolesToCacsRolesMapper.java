package com.jeppesen.jcms.customization.template.processing;

import com.jeppesen.jcms.customization.template.parsing.UserData;

public interface OldRolesToCacsRolesMapper {

	Iterable<String> getCacsRolesForUser(UserData user);

}
