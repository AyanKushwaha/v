package com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy;

import java.io.PrintStream;

import org.apache.xmlrpc.server.XmlRpcHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.webserver.WebServer;

import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers.DispatchingHandlerMapping;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers.RegexpHandlerMapping;
import com.jeppesensystems.carmen.crewweb.tools.xmlrpcserverproxy.handlers.recording.ProxyHandlerMapping;

/**
 * This is the main class of this project - the class you start the server with.
 */
public class XMLRPCMockServer {

	private Configuration config;
	
	public static void main(String[] args) {
		try {
			Configuration config = new Configuration(args);
			if (!config.correctlyConfigured()) {
				printHelp();
				throw new RuntimeException("Incorrect configuration/arguments");
			}
			new XMLRPCMockServer(config).start();
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(1);
		}
	}

	public XMLRPCMockServer(Configuration config) {
		this.config = config;
	}
	
	private void start() {
		print("XMLRPC Mock server starting using config: %s ", config);

		try {
			WebServer webServer = new WebServer(config.getPort());

			XmlRpcServer xmlRpcServer = webServer.getXmlRpcServer();

			XmlRpcHandlerMapping handlerMapping = new ProxyHandlerMapping(config);
			handlerMapping = new DispatchingHandlerMapping(handlerMapping, config.getFileLocator());
			handlerMapping = new RegexpHandlerMapping(handlerMapping, config);
			xmlRpcServer.setHandlerMapping(handlerMapping);

			// XmlRpcServerConfigImpl serverConfig = (XmlRpcServerConfigImpl)
			// xmlRpcServer.getConfig();
			// serverConfig.setEnabledForExtensions(true);
			// serverConfig.setContentLengthOptional(false);

			webServer.start();
			print("\nXMLRPC Server started\nRequest Log:");
		} catch (Exception e) {
			e.printStackTrace();
		}
	}


	private static void printHelp() {
		PrintStream o = System.out;
		o.println("Usage: XMLRPCMockServer [-noCache] -port <port> -backend <Carmencita|ReportServer|ReportServerCareer> [-delay maxDelay] -remoteHost <host> "
				+ "-remotePort <port> -cachePath <path>");
		o.println("----------------------------------------------------------------------------");
		o.println("The mock server will produce \"response\" files based on a real XMLRPC call to the remote server. Once");
		o.println("the file has been created it will be used for all identical/similar requests. This makes it possible to");
		o.println("record a scenario and then turn off the real backend server.");
		o.println("");
		o.println("The mock server also makes it possible to simulate long response times and random failure in order to");
		o.println("simulate a real world environment.");
		o.println("----------------------------------------------------------------------------");
	}

	private void print(String string, Object... args) {
		System.out.println(String.format(string, args));
	}
}
