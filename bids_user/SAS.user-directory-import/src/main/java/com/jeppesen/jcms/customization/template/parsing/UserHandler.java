package com.jeppesen.jcms.customization.template.parsing;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import com.jeppesen.jcms.customization.template.processing.UserProcessor;

/**
 * Creates {@link UserData} objects from the XML stream, and hands each {@link UserData} off to the
 * {@link UserProcessor} for processing.
 */
public class UserHandler extends DefaultHandler {

	private UserData user = null;

	boolean bRole = false;
	boolean bFirst_name = false;
	boolean bLast_name = false;
	boolean bUser_id = false;

	boolean isCrew = false;
	private final UserProcessor updater;
	private String roleName = "";

	public UserHandler(UserProcessor updater) {
		this.updater = updater;
	}

	@Override
	public void startElement(String uri, String localName, String qNamea, Attributes attributes) throws SAXException {
		String qName = removeNamespaceFromQName(qNamea);
		if (qName.equalsIgnoreCase("crew") && attributes.getLength() >= 4) {
			isCrew = true;

			String loginId = attributes.getValue("login_id");
			String userId = attributes.getValue("user_id");
			String password = attributes.getValue("password");
			String firstName = attributes.getValue("first_name");
			String lastName = attributes.getValue("last_name");
			String inactive = attributes.getValue("inactive");
			
			user = new UserData();

			user.setLoginId(loginId);
			user.setUserId(userId);
			user.setPassword(password);
			user.setFirstName(firstName);
			user.setLastName(lastName);
			// Inactive is an optional attribute, verify that it has been set.
			if (inactive != null) {
				user.setInactive(Boolean.parseBoolean(inactive));
			} else {
				user.setInactive(false);
			}
		} else if (qName.equalsIgnoreCase("role")) {
			// set boolean values for fields, will be used in setting user variables
			bRole = true;
		}
	}

	private String removeNamespaceFromQName(String qNamea) {
		String qName = qNamea.contains(":") ? qNamea.substring(qNamea.lastIndexOf(':') + 1) : qNamea;
		return qName;
	}

	@Override
	public void endElement(String uri, String localName, String qNamea) throws SAXException {
		String qName = removeNamespaceFromQName(qNamea);

		if (qName.equalsIgnoreCase("crew") && isCrew) {
			updater.processUser(user);
			isCrew = false;
		} else if (qName.equalsIgnoreCase("role")) {
			user.addRole(roleName.trim());
		}
		roleName = "";
	}

	@Override
	public void characters(char ch[], int start, int length) throws SAXException {
		if (bRole) {
			roleName += new String(ch, start, length);
		}
	}

}