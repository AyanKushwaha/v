package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers;

import org.apache.xmlrpc.XmlRpcRequest;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.PostProcessor;

public class PassthroughPostProcessor extends PostProcessor {

	@Override
	public String postProcessResult(String result, XmlRpcRequest request) {
		return result;
	}
}
