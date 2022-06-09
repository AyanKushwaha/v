package com.jeppesen.jcms.customization.template.parsing;

import java.io.IOException;
import java.io.InputStream;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.xml.sax.SAXException;

import com.jeppesen.jcms.customization.template.processing.UserDirectoryJdbcUpdater;

public class BidImportParser {

	private UserDirectoryJdbcUpdater updater;

	public BidImportParser(UserDirectoryJdbcUpdater updater) {
		this.updater = updater;
	}

	public void parseXML(InputStream in) {
		SAXParserFactory saxParserFactory = SAXParserFactory.newInstance();
		try {
			SAXParser saxParser = saxParserFactory.newSAXParser();
			UserHandler handler = new UserHandler(updater);
			saxParser.parse(in, handler);
		} catch (ParserConfigurationException | SAXException | IOException e) {
			e.printStackTrace();
		}
	}

}
