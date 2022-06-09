package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Date;
import java.util.regex.Pattern;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.XmlRpcHandler;
import org.apache.xmlrpc.XmlRpcRequest;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.postproc.PostProcessor;

public class Mapping implements XmlRpcHandler {

	private final Pattern compiledPattern;
	private final String fileName;
	private final PostProcessor postProcessor;

	public Mapping(Pattern compiledPattern, String fileName, PostProcessor postProcessor) {
		this.compiledPattern = compiledPattern;
		this.fileName = fileName;
		this.postProcessor = postProcessor;
	}

	public Pattern getCompiledPattern() {
		return compiledPattern;
	}

	@Override
	public Object execute(XmlRpcRequest request) throws XmlRpcException {
		String methodName = request.getMethodName();
		String tmpFileName = getNameOfResponseFile(request);

		System.out.println("Processing: " + methodName + " -> " + tmpFileName + " " + new Date());

		try {
			File file = locateResponseFileForThisRequest(tmpFileName);
			byte[] data = loadBytesFromResponseFile(file);
			String result = postProcessResponseData(request, data);
			return result;
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}

	public String getNameOfResponseFile(XmlRpcRequest request) {
		String methodName = request.getMethodName();
		String tmpFileName = fileName;
		if (methodName.equalsIgnoreCase("carmensystems.manpower.bids.jmp_crew_init")) {
			tmpFileName = getFileNameForSpecificAwardingType(request);
		}
		if (methodName.equalsIgnoreCase("carmensystems.manpower.bids.jmp_get_bid_list")) {
			tmpFileName = getFileNameForSpecificAwardingType(request);
		}
		if (methodName.equalsIgnoreCase("carmensystems.manpower.bids.jmp_create_bid")) {
			tmpFileName = getFileNameForSpecificAwardingType(request);
		}
		return tmpFileName;
	}

	private String postProcessResponseData(XmlRpcRequest request, byte[] data) {
		String result = new String(data);
		result = postProcessor.postProcessResult(result, request);
		return result;
	}

	private byte[] loadBytesFromResponseFile(File file) throws FileNotFoundException, IOException {
		FileInputStream stream = new FileInputStream(file);
		byte[] data = new byte[(int) file.length()];
		stream.read(data);
		stream.close();
		return data;
	}

	private File locateResponseFileForThisRequest(String tmpFileName) {
		File file = new File(tmpFileName);

		if (!file.exists()) {
			file = new File(System.getProperty("user.dir") + File.separator + tmpFileName);
		}
		if (!file.exists()) {
			file = new File(fileName);
		}
		if (!file.exists()) {
			file = new File(System.getProperty("user.dir") + File.separator + fileName);
		}
		return file;
	}

	// Private helper for multiple awarding types
	private String getFileNameForSpecificAwardingType(XmlRpcRequest request) {
		String xml = request.getParameter(0).toString();
		String everythingAfterAwardingType = xml.split("awardingType=")[1].substring(1);
		String awardingType = everythingAfterAwardingType.split("\"")[0].toLowerCase();
		return fileName.replaceFirst(".response", "_" + awardingType + ".response");
	}
}
