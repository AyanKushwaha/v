package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers;

import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.StringTokenizer;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.XmlRpcHandler;
import org.apache.xmlrpc.server.AbstractReflectiveHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcNoSuchHandlerException;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.util.FileLocator;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.util.PropertiesLoader;

/**
 * Parses a dispatch-mappings.properties files and prepares the server to serve
 * the methods defined in the mappings file.
 */
public class DispatchingHandlerMapping extends AbstractReflectiveHandlerMapping {

	private final XmlRpcHandlerMapping nextHandler;
	private Map<String, MethodDelegationHandler> methodMap;
	private FileLocator fileLocator;

	public DispatchingHandlerMapping(XmlRpcHandlerMapping nextHandler, FileLocator fileLocator) {
		this.nextHandler = nextHandler;
		this.fileLocator = fileLocator;

		System.out.println("Starting DispatchingHandlerMapping");

		Properties properties = new PropertiesLoader(fileLocator).loadMappingFile("dispatch-mappings.properties");
		initializeMappings(properties);
	}

	private void initializeMappings(Properties properties) {
		Enumeration<Object> keys = properties.keys();
		methodMap = new HashMap<String, MethodDelegationHandler>();

		while (keys.hasMoreElements()) {
			String key = (String) keys.nextElement();
			StringTokenizer stringTokenizer = new StringTokenizer(key, "-");

			String methodName = stringTokenizer.nextToken();
			String rootElement = stringTokenizer.nextToken();

			MethodDelegationHandler methodDelegationHandler = methodMap.get(methodName);
			if (methodDelegationHandler != null) {
				methodDelegationHandler.addMapping(rootElement, properties.getProperty(key));
			} else {
				methodDelegationHandler = new MethodDelegationHandler(fileLocator);
				methodMap.put(methodName, methodDelegationHandler);
				methodDelegationHandler.addMapping(rootElement, properties.getProperty(key));
			}
		}
	}

	@Override
	public XmlRpcHandler getHandler(String handlerName) throws XmlRpcNoSuchHandlerException, XmlRpcException {
		MethodDelegationHandler methodDelegationHandler = methodMap.get(handlerName);
		if (methodDelegationHandler != null) {
			return methodDelegationHandler;
		}

		System.out.println("No delegating handler found for: " + handlerName);

		return nextHandler.getHandler(handlerName);
	}
}
