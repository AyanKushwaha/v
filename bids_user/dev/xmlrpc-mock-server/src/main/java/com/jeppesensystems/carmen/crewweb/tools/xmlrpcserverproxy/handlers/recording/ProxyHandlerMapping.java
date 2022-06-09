package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers.recording;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.XmlRpcHandler;
import org.apache.xmlrpc.server.AbstractReflectiveHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcNoSuchHandlerException;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.Configuration;

/**
 * This is the recording main class - when this is used, the xml rpc server acts
 * as a "man in the middle" and relays all first requests to a real backend,
 * records the response and then later uses the response file instead of making
 * a real request the real backend server.
 */
public class ProxyHandlerMapping extends AbstractReflectiveHandlerMapping {

	private Configuration config;

	public ProxyHandlerMapping(Configuration config) {
		this.config = config;
	}

	/**
	 * Each request gets its own handler.
	 */
	@Override
	public XmlRpcHandler getHandler(String xmlRpcMethodName) throws XmlRpcNoSuchHandlerException, XmlRpcException {
		return new ProxyXmlRpcHandler(config, xmlRpcMethodName);
	}
}
