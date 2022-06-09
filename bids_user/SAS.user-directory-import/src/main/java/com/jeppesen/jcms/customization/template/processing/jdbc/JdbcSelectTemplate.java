package com.jeppesen.jcms.customization.template.processing.jdbc;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public abstract class JdbcSelectTemplate extends JdbcBaseTemplate {

	public JdbcSelectTemplate(Connection connection, String query) {
		super(connection, query);
	}

	protected void processResultSet(ResultSet resultSet) throws SQLException {
	}

	public void execute() {
		PreparedStatement statement = createPreparedStatement();
		try {
			doPrepare(statement);
			ResultSet resultSet = executeQuery(statement);
			try {
				doProcessResultSet(resultSet);
			} finally {
				closeResultSet(resultSet);
			}
		} finally {
			closeStatement(statement);
		}
	}

	private void doProcessResultSet(ResultSet resultSet) {
		try {
			processResultSet(resultSet);
		} catch (SQLException e) {
			throw ex("Failed to prepare SQL statement", e);
		}
	}

}
