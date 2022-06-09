package com.jeppesen.jcms.customization.template.processing.jdbc;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import org.jboss.logging.Logger;

public class JdbcBaseTemplate {

	private static final Logger LOG = Logger.getLogger(JdbcBaseTemplate.class);
	protected String query;
	protected Connection connection;

	public JdbcBaseTemplate(Connection connection, String query) {
		this.connection = connection;
		this.query = query;
	}

	protected void prepare(PreparedStatement pstmt) throws SQLException {
	}

	protected void doPrepare(PreparedStatement statement) {
		try {
			prepare(statement);
		} catch (SQLException e) {
			throw ex("Failed to prepare SQL statement", e);
		}
	}

	protected ResultSet executeQuery(PreparedStatement statement) {
		try {
			return statement.executeQuery();
		} catch (SQLException e) {
			throw ex("Failed to execute SQL query " + query, e);
		}
	}

	protected void closeResultSet(ResultSet resultSet) {
		if (resultSet != null) {
			try {
				resultSet.close();
			} catch (SQLException e) {
				throw ex("Failed to close resultset", e);
			}
		}
	}

	protected void closeStatement(PreparedStatement statement) {
		if (statement != null) {
			try {
				statement.close();
			} catch (SQLException e) {
				LOG.error("Failed to close PreparedStatement", e);
			}
		}
	}

	protected PreparedStatement createPreparedStatement() {
		try {
			PreparedStatement statement;
			statement = connection.prepareStatement(query);
			return statement;
		} catch (SQLException e) {
			throw ex("Failed to setup prepared statement", e);
		}
	}

	protected RuntimeException ex(String message, Throwable cause) {
		return new RuntimeException(message, cause);
	}

}
