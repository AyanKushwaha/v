package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.steps;

import org.apache.xmlrpc.XmlRpcRequest;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.PostProcessingStep;

/**
 * A simple post processing step that replaces all instances of KEY with VALUE,
 * where KEY is the string from {@link #getStringToSearchFor()} and VALUE is the
 * string from {@link #getReplacementString()}.
 */
public class StringReplacementPostProcessingStep implements PostProcessingStep {

	private String searchFor;
	private String replaceWith;

	public StringReplacementPostProcessingStep() {
	}

	public StringReplacementPostProcessingStep(String lookFor, String replaceWith) {
		this.searchFor = lookFor;
		this.replaceWith = replaceWith;
	}

	@Override
	public String postProcess(String result, XmlRpcRequest request) {
		return replaceAll(result, getStringToSearchFor(), getReplacementString(request));
	}
	
	protected String replaceAll(String input, String toLookFor, String toReplaceWith) {
		String regex = "\\$\\{" + toLookFor + "\\}";
		return input.replaceAll(regex, toReplaceWith);
	}

	protected String getReplacementString(XmlRpcRequest request) {
		return replaceWith;
	}

	protected String getStringToSearchFor() {
		return searchFor;
	}

}
