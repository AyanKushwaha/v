package com.jeppesen.jcms.customization.template.processing.jdbc;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public abstract class JdbcUpdateTemplate extends JdbcBaseTemplate {

	public JdbcUpdateTemplate(Connection connection, String query) {
		super(connection, query);
	}

	protected void verifyNumberOfRowsUpdate(int numberOfRowsUpdated) {
	}

	public void execute() {
		PreparedStatement statement = createPreparedStatement();
		try {
			doPrepare(statement);
			int numberOfRowsUpdated = executeUpdateQueryAndReturnNumberOfRowsUpdated(statement);
			verifyNumberOfRowsUpdate(numberOfRowsUpdated);
		} finally {
			closeStatement(statement);
		}
	}

	private int executeUpdateQueryAndReturnNumberOfRowsUpdated(PreparedStatement statement) {
		try {
			return statement.executeUpdate();
		} catch (SQLException e) {
			throw ex("Failed to execute query " + query, e);
		}
	}
}
