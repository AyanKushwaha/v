package com.jeppesen.jcms.customization.template.processing;

import java.sql.Connection;

public interface UserDirectoryFactory {

	public UserDirectory createUserDirectory(Connection connection);

}
