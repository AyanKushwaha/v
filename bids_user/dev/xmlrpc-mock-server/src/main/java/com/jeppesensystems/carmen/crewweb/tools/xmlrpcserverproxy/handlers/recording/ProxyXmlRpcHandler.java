package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers.recording;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.XmlRpcHandler;
import org.apache.xmlrpc.XmlRpcRequest;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.Configuration;

/**
 * This is the handler that either makes a call to the real back end server
 * (-remoteHost setting), or use a file from the "cache" if there's one that
 * matches the request that comes in.
 */
public class ProxyXmlRpcHandler implements XmlRpcHandler {

	private Configuration config;
	private String xmlRpcMethodName;

	public ProxyXmlRpcHandler(Configuration config, String xmlRpcMethodName) {
		this.config = config;
		this.xmlRpcMethodName = xmlRpcMethodName;
	}

	@Override
	public Object execute(XmlRpcRequest request) throws XmlRpcException {
		StringBuilder audit = new StringBuilder();
		audit.append("<request ");
		audit.append("method=\"" + xmlRpcMethodName + "\"");

		Object[] params = new Object[request.getParameterCount()];
		String requestId = calculateRequestId(request, params, audit);

		Object result = "response error";
		try {
			File file = getResponseFileForThisRequest(requestId);
			if (weShouldMakeRequestToRealBackendServer(file)) {
				if (config.useRemoteHost()) {
					result = getResultFromRealBackendServer(audit, params, file);
				} else {
					log("The server has been configured to run without remote server connection, unable to process request: "
							+ requestId);
					result = "";
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

		useArtificialDelayIfSoConfigured(audit);

		audit.append(" size=\"" + result.toString().length() + "\"");
		audit.append(" ts=\"" + System.currentTimeMillis() + "\"");
		audit.append("/>");

		log(audit.toString());

		return result;
	}

	public boolean weShouldMakeRequestToRealBackendServer(File file) {
		boolean makeRequest;
		if (!file.exists()) {
			log("No file to read cached response from");
			makeRequest = true;
		} else {
			if (config.useCache()) {
				log("Using cached response from file");
				makeRequest = false;
			} else {
				log("File with cached response exists, but cache is turned off");
				makeRequest = true;
			}
		}
		return makeRequest;
	}

	private Object getResultFromRealBackendServer(StringBuilder audit, Object[] params, File file) throws IOException,
			FileNotFoundException {
		boolean failed = false;
		Object result;
		try {
			XmlRpcClientConfigImpl xmlRpcClientConfig = new XmlRpcClientConfigImpl();
			xmlRpcClientConfig.setServerURL(this.config.getUrlToRemoteHost());
			XmlRpcClient client = new XmlRpcClient();
			client.setConfig(xmlRpcClientConfig);

			audit.append(" origin=\"XMLRPC\"");
			long xmlStartTime = System.nanoTime();
			result = client.execute(xmlRpcMethodName, params);
			long xmlStopTime = System.nanoTime();
			audit.append(" xmlrpc-duration=\"" + (xmlStopTime - xmlStartTime) / 1000000.0 + "\"");
		} catch (Exception e) {
			audit.append(" failed=\"Unable to execute XMLRPC call\"");
			result = "";
			failed = true;
			e.printStackTrace();
		}

		if (!failed) {
			file.createNewFile();
			FileWriter fw = new FileWriter(file);

			if (result instanceof String) {
				fw.write("TYPE: String\n");
				fw.write(result.toString());

			} else {
				fw.write("TYPE: Object\n");
				fw.close();

				// Append the object to the file...
				ObjectOutputStream os = new ObjectOutputStream(new FileOutputStream(file, true));
				os.writeObject(result);
				os.close();

			}
			fw.close();
		}
		return result;
	}

	private Object getResultFromResponseFile(StringBuilder audit, File file) throws FileNotFoundException, IOException,
			ClassNotFoundException {
		Object result;
		audit.append(" origin=\"CACHE\"");

		FileInputStream rawStream = new FileInputStream(file);
		BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(rawStream));

		String type = bufferedReader.readLine();
		if (type.equalsIgnoreCase("TYPE: String")) {
			String line = null;
			StringBuilder res = new StringBuilder();
			while ((line = bufferedReader.readLine()) != null) {
				res.append(line);
				res.append('\n');
			}
			result = res.toString();

		} else if (type.equalsIgnoreCase("TYPE: Object")) {
			// Reset the raw stream and forward to where the actual
			// object(s) are stored...
			bufferedReader.close();
			rawStream.close();
			rawStream = new FileInputStream(file);
			rawStream.skip(type.length() + 1);

			// Read the object(s) from the stream...
			ObjectInputStream os = new ObjectInputStream(rawStream);
			result = os.readObject();
			os.close();
		} else {
			log("Unable to load from cache: " + type);
			result = "";
		}
		bufferedReader.close();
		rawStream.close();
		return result;
	}

	private File getResponseFileForThisRequest(String requestId) {
		File file = config.getPathToCachedFile(requestId);
		log("Cache file for this request: " + file.getAbsolutePath());
		return file;
	}

	private String calculateRequestId(XmlRpcRequest request, Object[] params, StringBuilder audit) {
		StringBuilder id = new StringBuilder();
		id.append(xmlRpcMethodName);

		for (int i = 0; i < request.getParameterCount(); i++) {
			params[i] = request.getParameter(i);
			id.append("-");
			String part = params[i].toString();
			if (part.contains("<?xml")) {
				part = getRequestNameFromXml(part);
			} else if (part.length() > 10) {
				part = part.substring(0, 10);
			}
			id.append(part);
		}
		id.append(".response");
		String requestId = id.toString();

		audit.append(" key=\"" + requestId + "\"");

		return requestId;
	}

	private String getRequestNameFromXml(String part) {
		// we get
		// <?xml version="1.0" encoding="UTF-8" standalone="yes"?><ns7:crewInitRequest
		// we want crewInitRequest
		int secondTagStart = part.indexOf('<', part.indexOf('<') + 1);
		int tagNameEnd = part.indexOf(' ', secondTagStart);
		String tagName = part.substring(secondTagStart + 1, tagNameEnd);
		if (tagName.contains(":")) {
			int nameSpacePrefixEndsAt = tagName.indexOf(':');
			tagName = tagName.substring(nameSpacePrefixEndsAt + 1);
		}
		return tagName;
	}

	private void useArtificialDelayIfSoConfigured(StringBuilder audit) {
		if (config.useDelay()) {
			try {
				int sleep = (int) (Math.random() * config.getMaxDelay());
				audit.append(" pause=\"" + sleep + "\"");
				Thread.sleep(sleep);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	private void log(String string) {
		System.out.println(string);
	}

}
