package com.jeppesen.jcms.integrator.routes;

import static java.lang.String.format;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.util.UUID;

import javax.naming.InitialContext;
import javax.naming.NamingException;
import javax.sql.DataSource;

import org.apache.camel.Exchange;
import org.apache.camel.Message;
import org.apache.camel.Processor;
import org.apache.camel.component.file.GenericFile;
import org.jboss.logging.Logger;

import com.jeppesen.jcms.customization.sas.SASUserDirectoryFactory;
import com.jeppesen.jcms.customization.template.parsing.BidImportParser;
import com.jeppesen.jcms.customization.template.processing.UserDirectoryFactory;
import com.jeppesen.jcms.customization.template.processing.UserDirectoryJdbcUpdater;
import com.jeppesen.jcms.customization.template.processing.UserDirectoryTemplateFactory;

public class BidImportProcessor implements Processor {

	private static final String JNDI_NAME_OF_DATASOURCE = "java:jboss/datasources/CrewWebDS";
	private static final Logger LOG = Logger.getLogger(BidImportProcessor.class);

	@Override
	public void process(Exchange exchange) throws Exception {
		UUID jobId = UUID.randomUUID();
		LOG.info(format("User Directory Import job %s starting", jobId));
		try {
			doProcess(exchange);
			LOG.info(format("User Directory Import job %s completed", jobId));
		} catch (Exception e) {
			LOG.error(format("User Directory Import job %s failed to process bid import file", jobId), e);
			throw e;
		}
	}

	private void doProcess(Exchange exchange) throws FileNotFoundException {
		InputStream in = getInputStream(exchange);
		DataSource ds = getDataSource();
		UserDirectoryFactory factory = new SASUserDirectoryFactory();
		UserDirectoryTemplateFactory userDirectoryTemplateFactory = new UserDirectoryTemplateFactory(ds, factory);
		UserDirectoryJdbcUpdater updater = new UserDirectoryJdbcUpdater(userDirectoryTemplateFactory);
		BidImportParser parser = new BidImportParser(updater);
		parser.parseXML(in);
	}

	protected InputStream getInputStream(Exchange exchange) throws FileNotFoundException {
		Message message = exchange.getIn();
		Object body = message.getBody();
		@SuppressWarnings("rawtypes")
		File pathToFile = (File) ((GenericFile) body).getFile();
		LOG.info(format("User Directory Import start processing file %s", pathToFile.getAbsolutePath()));
		return new FileInputStream(pathToFile);
	}

	private DataSource getDataSource() {
		try {
			return (DataSource) new InitialContext().lookup(JNDI_NAME_OF_DATASOURCE);
		} catch (NamingException e) {
			throw new RuntimeException("Failed to lookup DataSource from " + JNDI_NAME_OF_DATASOURCE, e);
		}
	}
}
