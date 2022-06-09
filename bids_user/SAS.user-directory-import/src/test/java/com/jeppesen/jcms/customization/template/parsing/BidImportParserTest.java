package com.jeppesen.jcms.customization.template.parsing;

import java.io.FileInputStream;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import com.jeppesen.jcms.integrator.routes.BidImportProcessor;

public class BidImportParserTest {

	private BidImportProcessor testee;

	@Before
	public void setup() {

		testee = new BidImportProcessor();
	}

	@Test
	@Ignore
	public void testUserImport() throws Exception {
		FileInputStream fileInputStream = new FileInputStream("import.xml");
		// parser.parseXML(fileInputStream);
		//
		// assertThat("the size should be:", userObjectList.size(), equalTo(2));
		// assertThat("the first user login id should be:", userObjectList.get(0)
		// .getLoginId(), equalTo("123"));
		// assertThat("the first user login id should be:", userObjectList.get(0)
		// .getUserId(), equalTo("123"));
		// assertThat("the second user login id should be:", userObjectList.get(1)
		// .getLoginId(), equalTo("456"));
		// assertThat("the second user login id should be:", userObjectList.get(1)
		// .getUserId(), equalTo("456"));
	}

}
