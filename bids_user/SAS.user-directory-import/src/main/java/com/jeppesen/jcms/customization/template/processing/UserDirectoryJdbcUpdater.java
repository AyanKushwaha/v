package com.jeppesen.jcms.customization.template.processing;

import org.jboss.logging.Logger;

import com.jeppesen.jcms.customization.template.parsing.UserData;

public class UserDirectoryJdbcUpdater implements UserProcessor {

	private UserDirectoryTemplateFactory userDirectoryTemplateFactory;
	
	private static final Logger LOG = Logger.getLogger(UserDirectoryJdbcUpdater.class);

	public UserDirectoryJdbcUpdater(UserDirectoryTemplateFactory userDirectoryTemplateFactory) {
		this.userDirectoryTemplateFactory = userDirectoryTemplateFactory;
	}

	@Override
	public void processUser(final UserData user) {
		try {
			if (!user.isInactive()) {
				doProcess(user);
			} else {
				LOG.debug(String.format("Skipping user=%s due to inactive", user));
			}
		} catch (Exception e) {
			throw new RuntimeException("Failed to process " + user.toString(), e);
		}
	}

	private void doProcess(final UserData user) {
		userDirectoryTemplateFactory.createAndRun(new UserDirectoryProcessorCallback() {
			@Override
			public void withUserDirectory(UserDirectory userDirectory) {
				if (userDirectory.contains(user)) {
					userDirectory.updateUserInformation(user);
				} else {
					userDirectory.insertUserInformation(user);
				}
				userDirectory.dropAndCreateRolesFor(user);
			}
		});
	}

}
