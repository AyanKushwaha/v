package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc;

import org.apache.xmlrpc.XmlRpcRequest;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.steps.StringReplacementPostProcessingStep;

/**
 * Used with the Manpower backend. If method is "get_available_days_off" and category is "daysoff", let ${MONTH} be 9 or 10.
 */
public class AvailableDaysOffParameterReplacer extends StringReplacementPostProcessingStep {

	private static final int FIRST_ARGUMENT_CARRIES_REQUEST_XML_CONTENT = 0;

	public AvailableDaysOffParameterReplacer() {
		super("MONTH", "");
	}

	private boolean xmlRpcMethodIsGetAvailableDaysOff(XmlRpcRequest request) {
		String methodName = request.getMethodName();
		return "get_available_days_off".equals(methodName);
	}

	private boolean secondRequestParameterIsDaysOff(XmlRpcRequest request) {
		String requestPayload = (String) request.getParameter(FIRST_ARGUMENT_CARRIES_REQUEST_XML_CONTENT);
		return requestPayload.contains("category=\"daysoff\"");
	}

	@Override
	public String postProcess(String result, XmlRpcRequest request) {
		if (!xmlRpcMethodIsGetAvailableDaysOff(request)) {
			return result;
		}

		return super.postProcess(result, request);
	}

	@Override
	protected String getReplacementString(XmlRpcRequest request) {
		if (secondRequestParameterIsDaysOff(request)) {
			return "09";
		} else {
			return "10";
		}
	}

}
