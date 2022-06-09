package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.steps;

import org.apache.xmlrpc.XmlRpcRequest;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.PostProcessingStep;

public class RequestParameterReplacementStep implements PostProcessingStep {

	@Override
	public String postProcess(final String input, XmlRpcRequest request) {
		String result = input;
		for (int i = 0; i < request.getParameterCount(); i++) {
			result = replace(result, i, request.getParameter(i).toString());
		}
		return result;
	}

	private String replace(String input, int lookFor, String replaceWith) {
		String regex = "\\$\\{" + lookFor + "\\}";
		String result = input.replaceAll(regex, replaceWith);
		return result;
	}

}
