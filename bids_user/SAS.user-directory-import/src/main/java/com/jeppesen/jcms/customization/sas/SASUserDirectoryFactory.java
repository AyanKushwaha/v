package com.jeppesen.jcms.customization.sas;

import java.sql.Connection;

import com.jeppesen.jcms.customization.sas.parsing.SASUserDirectory;
import com.jeppesen.jcms.customization.template.processing.UserDirectory;
import com.jeppesen.jcms.customization.template.processing.UserDirectoryFactory;

public class SASUserDirectoryFactory implements UserDirectoryFactory {

	@Override
	public UserDirectory createUserDirectory(Connection connection) {
		return new SASUserDirectory(connection);
	}

}
