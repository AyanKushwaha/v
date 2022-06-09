package com.jeppesen.jcms.integrator.routes;

import static java.lang.String.format;

import javax.naming.InitialContext;
import javax.naming.NamingException;

import org.apache.camel.builder.RouteBuilder;
import org.jboss.logging.Logger;

public class UserDirectoryFromBidImportFileRouteBuilder extends RouteBuilder {

	private static final String JNDI_NAME = "java:global/jcms/customization/user-directory-import";
	private static final  Logger LOG = Logger.getLogger(UserDirectoryFromBidImportFileRouteBuilder.class);

	@Override
	public void configure() {
		final String path = getPathToDirectoryToWatch(JNDI_NAME);
		fromF("file:%s?move=processed", path).process(new BidImportProcessor());
		LOG.info(format("User Directory Import watching directory %s for new files", path));
	}

	private String getPathToDirectoryToWatch(String jndiName) {
		try {
			return (String) new InitialContext().lookup(jndiName);
		} catch (NamingException e) {
			throw new RuntimeException("Failed to lookup path to "
					+ "directory to watch for new import files, should be setup in " + JNDI_NAME, e);
		}
	}
}
