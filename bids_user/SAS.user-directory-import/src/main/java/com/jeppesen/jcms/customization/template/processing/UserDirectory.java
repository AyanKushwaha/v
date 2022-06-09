package com.jeppesen.jcms.customization.template.processing;

import com.jeppesen.jcms.customization.template.parsing.UserData;

public interface UserDirectory {

	boolean contains(UserData user);

	void insertUserInformation(UserData user);

	void dropAndCreateRolesFor(UserData user);

	void updateUserInformation(UserData user);

}
