package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy;

import java.io.File;
import java.net.MalformedURLException;
import java.net.URL;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.util.FileLocator;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.util.PropertiesLoader;

public class Configuration {

	private BackendServerType backendType;
	
	private int port = Integer.MIN_VALUE ;
	
	private String remoteHost;
	private int remotePort = Integer.MIN_VALUE ;
	private boolean noRemote;
	
	private FileLocator fileLocator;
	private boolean useCache;
	private File cachePath;

	private int maxDelay = Integer.MIN_VALUE;

	public Configuration(String[] args) {
		String tmpCachePath = null;
		for (int i = 0; i < args.length; i += 2) {
			String arg = args[i];

			if (arg.equalsIgnoreCase("-port")) {
				port = Integer.parseInt(args[i + 1]);

			} else if (arg.equalsIgnoreCase("-backend")) {
				String backendServerType = args[i + 1];
				if (backendServerType.equalsIgnoreCase("Carmencita")) {
					backendType = BackendServerType.CARMENCITA;
				} else if (backendServerType.equalsIgnoreCase("ReportServer")) {
					backendType = BackendServerType.REPORT_SERVER;
				} else if (backendServerType.equalsIgnoreCase("ReportServerCareer")) {
					backendType = BackendServerType.REPORT_SERVER_CAREER;
				} else {
					backendServerType = "Invalid!!";
				}

			} else if (arg.equalsIgnoreCase("-delay")) {
				maxDelay = Integer.parseInt(args[i + 1]);

			} else if (arg.equalsIgnoreCase("-remoteHost")) {
				remoteHost = args[i + 1];

			} else if (arg.equalsIgnoreCase("-remotePort")) {
				remotePort = Integer.parseInt(args[i + 1]);

			} else if (arg.equalsIgnoreCase("-cachePath")) {
				tmpCachePath = args[i + 1];

			} else if (arg.equalsIgnoreCase("-noCache")) {
				useCache = false;

			} else if (arg.equalsIgnoreCase("-noRemote")) {
				noRemote = true;

			} else {
				throw new IllegalArgumentException("Unknown argument: " + arg);
			}
		}

		if (tmpCachePath != null) {
			File dir = new File(tmpCachePath);
			if (dir.exists() && dir.isDirectory()) {
				cachePath = dir;
			}
		}

		if (port == Integer.MIN_VALUE) {
			port = 7311;
		}

		if (cachePath == null) {
			cachePath = null;
			useCache = false;
		}

		if (remoteHost == null || remotePort == Integer.MIN_VALUE) {
			noRemote = true;
		}

		fileLocator = new FileLocator(cachePath);
	}

	public boolean correctlyConfigured() {
		return !hasConfigurationIssues();
	}

	private boolean hasConfigurationIssues() {
		return port == Integer.MIN_VALUE || cachePath == null || backendType == null
				|| ((remoteHost == null || remotePort == Integer.MIN_VALUE) && noRemote != true);
	}

	public int getPort() {
		return port;
	}

	public FileLocator getFileLocator() {
		return fileLocator;
	}

	public boolean useRemoteHost() {
		return !noRemote;
	}

	public boolean useCache() {
		return useCache;
	}

	public URL getUrlToRemoteHost() throws MalformedURLException {
		return new URL("http://" + remoteHost + ":" + remotePort + "/RPC2");
	}

	public File getPathToCachedFile(String fileName) {
		return new File(cachePath, fileName);
	}

	public boolean useDelay() {
		return maxDelay != Integer.MIN_VALUE;
	}

	public int getMaxDelay() {
		return maxDelay;
	}

	public PropertiesLoader getPropertiesLoader() {
		return new PropertiesLoader(getFileLocator());
	}

	public BackendServerType getBackendType() {
		return backendType;
	}

}
