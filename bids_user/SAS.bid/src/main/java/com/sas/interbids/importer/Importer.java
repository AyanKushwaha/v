package com.sas.interbids.importer;

import java.io.Closeable;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;

import javax.naming.InitialContext;
import javax.naming.NamingException;

import org.apache.commons.io.IOUtils;

import com.jeppesen.carmen.crewweb.framework.bo.ImportData;
import com.jeppesen.carmen.crewweb.framework.bo.impl.ImportDataImpl;
import com.jeppesen.carmen.crewweb.framework.context.aware.JAXBTranslatorAware;
import com.jeppesen.carmen.crewweb.framework.customization.ImportProcessor;
import com.jeppesen.carmen.crewweb.framework.util.JAXBTranslator;
import com.jeppesen.carmen.crewweb.framework.xmlschema._import.ImportSchemaType;
import com.jeppesen.jcms.crewweb.common.context.aware.FileLoaderUtilAware;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;
import com.jeppesen.jcms.crewweb.common.util.CWLog;
import com.jeppesen.jcms.crewweb.common.util.FileContent;
import com.jeppesen.jcms.crewweb.common.util.FileDescriptor;
import com.jeppesen.jcms.crewweb.common.util.FileLoaderUtil;

public class Importer implements ImportProcessor, FileLoaderUtilAware, JAXBTranslatorAware {

	/**
	 * The file loader to use when loading file content.
	 */
	private FileLoaderUtil fileLoaderUtil;

	/**
	 * The JAXB unmarshaller to use when processing import files.
	 */
	private JAXBTranslator unmarshaller;

	/**
	 * The folder that the user directory importer is monitoring.
	 */
	private File userDirectoryImportFolder;
	private File tmpUserDirectoryImportFolder;

	public Importer() {
		String jndiName = "java:global/jcms/customization/user-directory-import";
		try {
			String path = (String) new InitialContext().lookup(jndiName);
			userDirectoryImportFolder = new File(path);
			if (!userDirectoryImportFolder.exists() || !userDirectoryImportFolder.isDirectory()) {
				throw new RuntimeException("User Directory Import folder is not an existing folder: " + path);
			}
			
			tmpUserDirectoryImportFolder = new File(userDirectoryImportFolder, ".tmp");
			if (!tmpUserDirectoryImportFolder.exists() && userDirectoryImportFolder.canWrite()) {
				if (!tmpUserDirectoryImportFolder.mkdir()) {
					throw new RuntimeException("Unable to create temporary user directory import path: " + tmpUserDirectoryImportFolder.getPath());
				}
			}
		} catch (NamingException e) {
			throw new RuntimeException("Failed to lookup " + jndiName, e);
		}
	}

	@Override
	public void setFileLoaderUtil(final FileLoaderUtil fileLoaderUtil) {
		this.fileLoaderUtil = fileLoaderUtil;
	}

	@Override
	public void setJAXBTranslator(JAXBTranslator unmarshaller) {
		this.unmarshaller = unmarshaller;
	}

	@Override
	public ImportData process(FileDescriptor file) {
		if (file == null) {
			throw new CWRuntimeException("Unable to process 'null' file!");
		}

		File copy = duplicateFileForUserDirectoryProcessing(file);
		FileContent content = fileLoaderUtil.getFileContent(file);
		ImportSchemaType jaxbData = unmarshalXML(content.getContent());

		moveDuplicateFileIntoCorrectFolder(file, copy);

		return createWrapper(jaxbData);
	}

	private void moveDuplicateFileIntoCorrectFolder(FileDescriptor file, File copy) {
		File destination = calculateNameForUserDirectoryImportFile(file);
		String logMessage = String.format("Copied import file %s to %s", file.getName(),
				destination.getAbsolutePath());
		CWLog.getLogger(Importer.class).info(logMessage);
		try {
			Files.move(copy.toPath(), destination.toPath(), StandardCopyOption.ATOMIC_MOVE);
		} catch (IOException e) {
			throw new CWRuntimeException("Unable to copy import file " + file.getName()
					+ " for user directory import - aborting", e);
		}		
	}
	
	private File duplicateFileForUserDirectoryProcessing(FileDescriptor file) {
		try {
			File copy = new File(tmpUserDirectoryImportFolder.getAbsolutePath(), file.getName());
			FileInputStream from = new FileInputStream(file.getAbsolutePath());
			FileOutputStream to = new FileOutputStream(copy.getAbsolutePath());
			try {
				IOUtils.copyLarge(from, to);
				return copy;
			} finally {
				close(from);
				close(to);
			}
		} catch (IOException e) {
			throw new CWRuntimeException("Unable to copy import file " + file.getName()
					+ " from "+ file.getAbsolutePath() +" to " + tmpUserDirectoryImportFolder.getAbsolutePath() + "for user directory import - aborting", e);
		}

	}

	private void close(Closeable stream) {
		try {
			stream.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	private File calculateNameForUserDirectoryImportFile(FileDescriptor file) {
		return new File(userDirectoryImportFolder, file.getName());
	}

	/**
	 * Create the JAXB wrapper object to allow for easier processing.
	 * 
	 * @param jaxbData
	 *            the JAXB data.
	 * @return the wrapped JAXB object.
	 */
	private ImportData createWrapper(ImportSchemaType jaxbData) {
		return new ImportDataImpl(jaxbData);
	}

	/**
	 * Invoke the unmarshaller to transform the XML to POJO.
	 * 
	 * @param xml
	 *            the import XML.
	 * @return a JAXB structure.
	 */
	private ImportSchemaType unmarshalXML(byte[] xml) {
		return unmarshaller.unmarshal(xml, ImportSchemaType.class);
	}

}
