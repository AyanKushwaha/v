package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.util;

import java.io.File;

/**
 * To be backwards compatible, we'll look for the file in three placesToLookIn: 
 * cachePath, user's home directory and fall back to current working directory as last resort.
 */
public class FileLocator {

	private final File[] placesToLookIn;

	public FileLocator(File cacheDirectory) {
		placesToLookIn = new File[] { cacheDirectory, new File(System.getProperty("user.dir")) };
	}

	public File locateFile(String fileName) {
		for (File dir : placesToLookIn) {
			File file = new File(dir, fileName);
			if (file.exists()) {
				return file;
			}
		}
		return new File(fileName);
	}

}
