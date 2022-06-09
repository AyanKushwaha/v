package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers;

import java.io.File;
import java.io.FileInputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.StringTokenizer;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.XmlRpcHandler;
import org.apache.xmlrpc.XmlRpcRequest;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.util.FileLocator;

public class MethodDelegationHandler implements XmlRpcHandler {
    
    private final Map<String, String> rootElementFileRefMap;
	private final FileLocator fileLocator;

    public MethodDelegationHandler(FileLocator fileLocator) {
		rootElementFileRefMap = new HashMap<>();
		this.fileLocator = fileLocator;
    }

    public Object execute(XmlRpcRequest request) throws XmlRpcException {
        request.getParameterCount();

        Object parameter = request.getParameter(0);
        if (parameter != null) {
            String xmlString = (String) parameter;
            StringTokenizer stringTokenizer = new StringTokenizer(xmlString, "<");
            stringTokenizer.nextToken();
            String messageRoot = stringTokenizer.nextToken();
            stringTokenizer = new StringTokenizer(messageRoot, " ");

            String rootElement = stringTokenizer.nextToken();
            if (rootElement.contains(":")) { //namespace
                rootElement = rootElement.split(":")[1]; 
            }
            String fileName = rootElementFileRefMap.get(rootElement);

            try {
                File file = fileLocator.locateFile(fileName);

                FileInputStream stream = new FileInputStream(file);
                byte[] data = new byte[(int) file.length()];
                stream.read(data);
                stream.close();

                String result = new String(data);
                return result;

            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        return null;
    }

    public void addMapping(String rootElementName, String fileRef) {
        rootElementFileRefMap.put(rootElementName, fileRef);
    }

}
