package com.jeppesen.jcms.customization.sas.parsing;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import com.jeppesen.jcms.customization.template.parsing.UserData;
import com.jeppesen.jcms.customization.template.processing.OldRolesToCacsRolesMapper;
import com.jeppesen.jcms.customization.template.processing.UserDirectory;
import com.jeppesen.jcms.customization.template.processing.jdbc.JdbcSelectTemplate;
import com.jeppesen.jcms.customization.template.processing.jdbc.JdbcUpdateTemplate;

public class SASUserDirectory implements UserDirectory {

	private static final String USERDIRECTORY_INSERT = "INSERT INTO userdirectory (userId, password, firstName, lastName) VALUES (?, ?, ?, ?)";
	private static final String USERDIRECTORY_UPDATE = "UPDATE userdirectory SET password=?, firstName=?, lastName=? WHERE userId=?";
	private static final String USERDIRROLES_DELETE = "DELETE FROM userdirroles WHERE userid=?";
	private static final String USERDIRROLES_INSERT = "INSERT INTO userdirroles (userid, roletype, name, value) VALUES (?, ?, ?, ?)";

	private Connection connection;
	private OldRolesToCacsRolesMapper roleMapper = new SASRoleMapper();

	public SASUserDirectory(Connection connection) {
		this.connection = connection;
	}

	@Override
	public boolean contains(final UserData user) {
		final boolean[] userExists = new boolean[1];
		new JdbcSelectTemplate(connection, "SELECT COUNT(userid) FROM userdirectory WHERE userid=?") {
			@Override
			protected void prepare(PreparedStatement pstmt) throws SQLException {
				pstmt.setString(1, user.getLoginId());
			}

			@Override
			protected void processResultSet(ResultSet resultSet) throws SQLException {
				resultSet.next();
				int count = resultSet.getInt(1);
				userExists[0] = count == 1;
			}
		}.execute();
		return userExists[0];
	}

	@Override
	public void insertUserInformation(final UserData user) {
		new JdbcUpdateTemplate(connection, USERDIRECTORY_INSERT) {
			@Override
			protected void prepare(PreparedStatement pstmt) throws SQLException {
				pstmt.setString(1, user.getLoginId());
				pstmt.setString(2, user.getPassword());
				pstmt.setString(3, user.getFirstName());
				pstmt.setString(4, user.getLastName());
			}
		}.execute();
	}

	@Override
	public void dropAndCreateRolesFor(final UserData user) {
		dropAllRolesFor(user);
		insertRolesFor(user);
		insertCrewIdentityAttributeFor(user);
	}

	private void insertCrewIdentityAttributeFor(final UserData user) {
		new JdbcUpdateTemplate(connection, USERDIRROLES_INSERT) {
			@Override
			protected void prepare(PreparedStatement pstmt) throws SQLException {
				pstmt.setString(1, user.getLoginId());
				pstmt.setString(2, "attribute");
				pstmt.setString(3, "crewIdentity");
				pstmt.setString(4, user.getUserId());
			}
		}.execute();
	}

	private void insertRolesFor(final UserData user) {
		for (final String cacsRole : roleMapper.getCacsRolesForUser(user)) {
			new JdbcUpdateTemplate(connection, USERDIRROLES_INSERT) {
				@Override
				protected void prepare(PreparedStatement pstmt) throws SQLException {
					pstmt.setString(1, user.getLoginId());
					pstmt.setString(2, "role");
					pstmt.setString(3, "role");
					pstmt.setString(4, cacsRole);
				}
			}.execute();
		}
	}

	private void dropAllRolesFor(final UserData user) {
		new JdbcUpdateTemplate(connection, USERDIRROLES_DELETE) {
			@Override
			protected void prepare(PreparedStatement pstmt) throws SQLException {
				pstmt.setString(1, user.getLoginId());
			}
		}.execute();
	}

	@Override
	public void updateUserInformation(final UserData user) {
		new JdbcUpdateTemplate(connection, USERDIRECTORY_UPDATE) {
			@Override
			protected void prepare(PreparedStatement pstmt) throws SQLException {
				pstmt.setString(1, user.getPassword());
				pstmt.setString(2, user.getFirstName());
				pstmt.setString(3, user.getLastName());
				pstmt.setString(4, user.getLoginId());
			}
		}.execute();
	}

}
