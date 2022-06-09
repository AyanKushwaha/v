package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers;

import java.io.File;
import java.util.Collection;
import java.util.HashMap;
import java.util.Properties;
import java.util.Set;
import java.util.regex.Pattern;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.XmlRpcHandler;
import org.apache.xmlrpc.server.AbstractReflectiveHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcNoSuchHandlerException;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.BackendServerType;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.Configuration;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.AvailableDaysOffParameterReplacer;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.PostProcessor;

public class RegexpHandlerMapping extends AbstractReflectiveHandlerMapping {

	private static final String MAPPING_PREFIX = "mapping-";
	private static final String MAPPING_REGEXP_POSTFIX = "-regexp";
	private static final String MAPPING_FILE_POSTFIX = "-file";
	private static final String MAPPING_FILE_POSTPROCESS = "-postprocess";

	private final XmlRpcHandlerMapping nextHandler;
	private Configuration config;
	private Properties properties;
	private HashMap<Integer, Mapping> mappings = new HashMap<Integer, Mapping>();

	public void loadMapping() {
		System.out.println("Starting RegexpHandlerMapping");
		String propertiesFileName = null;
		// IMPROVEMENT: remove this and use the "name" instead
		BackendServerType backendType = config.getBackendType();
		if (backendType == BackendServerType.CARMENCITA) {
			propertiesFileName = "carmencita-mappings.properties";
		} else if (backendType == BackendServerType.REPORT_SERVER) {
			propertiesFileName = "report-server-mappings.properties";
		} else if (backendType == BackendServerType.REPORT_SERVER_CAREER) {
			propertiesFileName = "report-server-career-mappings.properties";
		}

		properties = config.getPropertiesLoader().loadMappingFile(propertiesFileName);
		createRegexpMappings();
	}

	public RegexpHandlerMapping(XmlRpcHandlerMapping handlerMapping, Configuration config) {
		nextHandler = handlerMapping;
		this.config = config;
		loadMapping();
	}

	private void createRegexpMappings() {
		Set<Object> keySet = properties.keySet();
		for (Object object : keySet) {
			String key = String.valueOf(object);
			if (key.startsWith(MAPPING_PREFIX) && key.endsWith(MAPPING_REGEXP_POSTFIX)) {
				String substring = key.substring(MAPPING_PREFIX.length(),
						key.length() - MAPPING_REGEXP_POSTFIX.length());
				int number = Integer.valueOf(substring);
				createRegexpMapping(number);
			}
		}
	}

	private void createRegexpMapping(int number) {
		String regexp = (String) properties.get(MAPPING_PREFIX + number + MAPPING_REGEXP_POSTFIX);
		String fileName = (String) properties.get(MAPPING_PREFIX + number + MAPPING_FILE_POSTFIX);
		File file = config.getPathToCachedFile(fileName);
		Pattern compiledPattern = Pattern.compile(regexp);
		PostProcessor postProcessor = createPostProcessor(number);

		System.out.println(regexp + "=" + file.getAbsolutePath());
		mappings.put(number, new Mapping(compiledPattern, file.getAbsolutePath(), postProcessor));
	}

	public boolean usePostProcessingForMapping(int number) {
		boolean postProcess = Boolean.valueOf((String) properties.get(MAPPING_PREFIX + number
				+ MAPPING_FILE_POSTPROCESS));
		return postProcess;
	}

	private PostProcessor createPostProcessor(int number) {
		if (usePostProcessingForMapping(number)) {
			// we could read in custom post processors here per mapping
			PostProcessor postProcessor = new PostProcessor();
			postProcessor.addPostProcessingStep(new AvailableDaysOffParameterReplacer());
			return postProcessor;
		} else {
			return new PassthroughPostProcessor();
		}
	}

	@Override
	public XmlRpcHandler getHandler(String xmlRpcMethodName) throws XmlRpcNoSuchHandlerException, XmlRpcException {
		// See if any of our mappings matches the xml rpc method name
		Collection<Mapping> values = mappings.values();
		for (Mapping mapping : values) {
			if (mapping.getCompiledPattern().matcher(xmlRpcMethodName).matches()) {
				return mapping;
			}
		}

		System.out.println("No regexp handler for: " + xmlRpcMethodName);

		return nextHandler.getHandler(xmlRpcMethodName);
	}
}
