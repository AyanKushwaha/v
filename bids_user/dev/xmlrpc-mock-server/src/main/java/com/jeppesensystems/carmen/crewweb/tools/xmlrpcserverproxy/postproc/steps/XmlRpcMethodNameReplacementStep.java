package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.steps;

import org.apache.xmlrpc.XmlRpcRequest;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.PostProcessingStep;

public class XmlRpcMethodNameReplacementStep implements PostProcessingStep {

	@Override
	public String postProcess(String result, XmlRpcRequest request) {
		return result.replaceAll("\\$\\{METHOD\\}", request.getMethodName());
	}

}
