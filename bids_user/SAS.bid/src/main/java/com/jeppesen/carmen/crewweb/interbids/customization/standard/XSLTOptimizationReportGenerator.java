package com.jeppesen.carmen.crewweb.interbids.customization.standard;

import java.io.InputStream;
import java.io.StringReader;

import javax.xml.XMLConstants;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamSource;

import org.apache.commons.io.output.ByteArrayOutputStream;

import com.jeppesen.carmen.crewweb.backendfacade.bo.OptimizationOnDemandJob;
import com.jeppesen.carmen.crewweb.framework.reports.Report;
import com.jeppesen.carmen.crewweb.framework.util.BidResourceLocator;
import com.jeppesen.carmen.crewweb.interbids.customization.OptimizationReportGenerator;
import com.jeppesen.jcms.crewweb.common.context.ResourceLocator;
import com.jeppesen.jcms.crewweb.common.context.aware.ResourceLocatorAware;
import com.jeppesen.jcms.crewweb.common.exception.CWException;
import com.jeppesen.jcms.crewweb.common.util.CWLog;


/**
 * This class implements the default optimization report generator based on XML/XSLT logic. It reads the
 * "optimization_report.xsl" from the resources and injects a big XML structure.
 * <p>
 * Example:
 * 
 * <pre>
 * {@code
 * &lt;request id='&lt;request-id&gt;' backendRequestId='&lt;request-id&gt;' submitted='2009-01-01 13:55' 
 *   finished='2009-01-01 13:57' userId='&lt;userid&gt;' requestType=''/&gt;
 *   &lt;requestData&gt;
 *     &lt;![CDATA[
 *       === The entire request data submitted to the backend server (ETAB format). ===
 *     ]]&gt;
 *   &lt;/requestData&gt;
 *   &lt;response&gt;
 *     === The entire result XML comming from the backend server. ===
 *   &lt;/response&gt;
 * &lt;/request&gt;
 * }
 * </pre>
 */
public class XSLTOptimizationReportGenerator implements OptimizationReportGenerator, ResourceLocatorAware {

    /**
     * The name of the XSL report to use when transforming the XML to HTML.
     */
    protected static final String OPTIMIZATION_REPORT_XSL = "optimization_report.xsl";

    /**
     * The logger for this class.
     */
    private static final CWLog LOG = CWLog.getLogger(XSLTOptimizationReportGenerator.class);

    /**
     * NEWLINE String.
     */
    private static final String NEWLINE = "\n";

    /**
     * The resource locator to use when loading XSL files.
     */
    private ResourceLocator resourceLocator;

    /**
     * {@inheritDoc}
     */
    public Report generateReport(OptimizationOnDemandJob request) throws CWException {

        // Populate the XML structure.
        StringBuilder xml = new StringBuilder();
        xml.append("<request");
        xml.append(" id='" + request.getId() + "'");
        xml.append(" backendRequestId='" + request.getBackendRequestId() + "'");
        xml.append(">");
        xml.append(NEWLINE);

        // Add request data.
        String requestData = request.getRequestData();
        if (requestData != null) {
            xml.append("<requestData><![CDATA[");
            xml.append(NEWLINE);
            xml.append(requestData);
            xml.append(NEWLINE);
            xml.append("]]></requestData>");
            xml.append(NEWLINE);
        }

        // Add request data.
        String referenceData = request.getReferenceData();
        if (referenceData != null) {
            xml.append("<referenceData><![CDATA[");
            xml.append(NEWLINE);
            xml.append(referenceData);
            xml.append(NEWLINE);
            xml.append("]]></referenceData>");
            xml.append(NEWLINE);
        }

        // Add backend server response.
        String requestResult = request.getRequestResult();
        if (requestResult != null) {
            xml.append("<response>");
            xml.append(request.getRequestResult());
            xml.append("</response>");
            xml.append(NEWLINE);
        }

        // Close the XML structure.
        xml.append("</request>");

        // Execute the XSLT.
        TransformerFactory factory = TransformerFactory.newInstance();
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
        factory.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
        String xslFileName = OPTIMIZATION_REPORT_XSL;

        Transformer newTransformer;
        try {
            InputStream xslStream = ((BidResourceLocator) resourceLocator).findXSLStream(xslFileName);
            newTransformer = factory.newTransformer(new StreamSource(xslStream));
        } catch (Exception e) {
            LOG.error("Unable to initialize the transformer based on the XSLT resource name! " + xslFileName, e);
            throw new CWException(-1, "Unable to initialize the transformer based on the XSLT resource name! "
                    + xslFileName, e);
        }

        XSLTOptimizationReport generatedReport = null;

        try {
            // Perform the transformation.
            javax.xml.transform.Source xmlSource = new javax.xml.transform.stream.StreamSource(new StringReader(xml
                    .toString()));

            ByteArrayOutputStream output = new ByteArrayOutputStream();
            javax.xml.transform.Result result = new javax.xml.transform.stream.StreamResult(output);
            newTransformer.transform(xmlSource, result);

            generatedReport = new XSLTOptimizationReport();
            generatedReport.setContent(output.toByteArray());
        } catch (Exception e) {
            LOG.error("Unable to transform the XML using the XSLT transformer!", e);
            throw new CWException(-1, "Unable to transform the XML using the XSLT transformer: " + e.getMessage(), e);
        }

        return generatedReport;
    }

    /**
     * Set the resource locator reference.
     * 
     * @param resourceLocator the resource locator reference.
     */
    public void setResourceLocator(ResourceLocator resourceLocator) {
        this.resourceLocator = resourceLocator;
    }

}
