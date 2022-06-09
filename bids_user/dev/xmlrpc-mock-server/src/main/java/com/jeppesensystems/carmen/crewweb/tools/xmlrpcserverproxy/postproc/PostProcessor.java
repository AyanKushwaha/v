package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc;

import java.util.ArrayList;
import java.util.Collection;
import java.util.UUID;

import org.apache.xmlrpc.XmlRpcRequest;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.steps.RequestParameterReplacementStep;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.steps.StringReplacementPostProcessingStep;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.steps.XmlRpcMethodNameReplacementStep;

/**
 * Takes a string and replaces all "${X}" with "Y", where X and Y comes from a
 * {@link PostProcessingInstructor}.
 */
public class PostProcessor {

	private Collection<PostProcessingStep> steps = new ArrayList<>();

	public PostProcessor() {
		setupDefaultParameterReplacers();
	}

	public String postProcessResult(String result, XmlRpcRequest request) {
		for (PostProcessingStep step : steps) {
			result = step.postProcess(result, request);
		}

		return result;
	}

	public void addPostProcessingStep(PostProcessingStep processingStep) {
		steps.add(processingStep);
	}

	protected void setupDefaultParameterReplacers() {
		// Replace all ${0..n} with the parameters from the request.
		addPostProcessingStep(new RequestParameterReplacementStep());

		// Replace all ${METHOD} with the name of the XMLRPC method name
		addPostProcessingStep(new XmlRpcMethodNameReplacementStep());
		
		// Replace all ${UUID} with a unique UUID.
		addPostProcessingStep(new StringReplacementPostProcessingStep("UUID", getUuid()));

		// Replace all ${TIMESTAMP} with a System.nanoTime();
		addPostProcessingStep(new StringReplacementPostProcessingStep("TIMESTAMP", getTimestamp()));
	}

	protected String getUuid() {
		return UUID.randomUUID().toString();
	}

	protected String getTimestamp() {
		return "" + System.nanoTime();
	}

}
