package com.jeppesen.jcms.customization.template.processing;

import java.sql.Connection;
import java.sql.SQLException;

import javax.sql.DataSource;

import org.jboss.logging.Logger;

public class UserDirectoryTemplateFactory {

	private static final Logger LOG = Logger.getLogger(UserDirectoryTemplateFactory.class);
	private final DataSource ds;
	private final UserDirectoryFactory userDirectoryFactory;

	public UserDirectoryTemplateFactory(DataSource ds, UserDirectoryFactory factory) {
		this.ds = ds;
		this.userDirectoryFactory = factory;
	}

	public void createAndRun(UserDirectoryProcessorCallback userDirectoryProcessorCallback) {
		Connection connection = null;
		try {
			connection = getConnection();
			UserDirectory directory = userDirectoryFactory.createUserDirectory(connection);
			userDirectoryProcessorCallback.withUserDirectory(directory);
			commit(connection);
		} catch (Exception e) {
			rollBack(connection);
		} finally {
			closeConnection(connection);
		}
	}

	private void rollBack(Connection connection) {
		if (connection != null) {
			try {
				connection.rollback();
			} catch (SQLException e) {
				throw new RuntimeException("Failed to rollback SQL transaction", e);
			}
		}
	}

	private void commit(Connection connection) {
		try {
			connection.commit();
		} catch (SQLException e) {
			throw new RuntimeException("Failed to commit SQL transaction", e);
		}
	}

	private void closeConnection(Connection connection) {
		if (connection != null) {
			try {
				connection.close();
			} catch (SQLException e) {
				LOG.error("Failed to close JDBC connection", e);
			}
		}
	}

	private Connection getConnection() {
		try {
			Connection connection = ds.getConnection();
			connection.setAutoCommit(false);
			return connection;
		} catch (SQLException e) {
			throw new RuntimeException("Failed to acquire connection to database", e);
		}
	}

}
