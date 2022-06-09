package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.util;

import java.io.File;
import java.io.FileInputStream;
import java.util.Properties;

public class PropertiesLoader {

	private final FileLocator fileLocator;
	
	public PropertiesLoader(FileLocator fileLocator) {
		this.fileLocator = fileLocator;
	}

	public Properties loadMappingFile(String fileName) {
		return loadMappingFile(fileLocator.locateFile(fileName));
	}

	private Properties loadMappingFile(File propertiesFile) {
		System.out.println("Loading mappings from \"" + propertiesFile.getAbsolutePath());
		try {
			Properties p = new Properties();
            p.load(new FileInputStream(propertiesFile));
            return p;
        } catch (Exception e) {
            throw new IllegalStateException("Unable to load the \"" + propertiesFile.getName() + "\" file", e);
        }
	}

}
