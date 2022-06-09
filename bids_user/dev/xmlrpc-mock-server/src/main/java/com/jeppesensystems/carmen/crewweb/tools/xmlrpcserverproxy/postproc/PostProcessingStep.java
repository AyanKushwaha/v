package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc;

import org.apache.xmlrpc.XmlRpcRequest;

public interface PostProcessingStep {

	String postProcess(String result, XmlRpcRequest request);

}
