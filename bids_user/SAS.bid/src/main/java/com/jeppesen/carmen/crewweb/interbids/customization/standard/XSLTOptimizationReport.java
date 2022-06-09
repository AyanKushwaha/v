package com.jeppesen.carmen.crewweb.interbids.customization.standard;

import java.io.ByteArrayInputStream;
import java.io.InputStream;

import org.joda.time.DateTime;

import com.jeppesen.carmen.crewweb.framework.reports.Report;
import com.jeppesen.carmen.crewweb.framework.reports.ReportAccessLevel;
import com.jeppesen.jcms.crewweb.common.exception.CWException;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;

/**
 * This class contains the standard optimization report implementation. Should only be used by classes in the
 * customization layer.
 */
public class XSLTOptimizationReport implements Report {

    /**
     * The report MIME type.
     */
    private static final String OPTIMIZATION_REPORT_MIMETYPE = "text/html";

    /**
     * The report type.
     */
    private static final String OPTIMIZATION_REPORT_TYPE = "optimization";

    /**
     * The content of the report.
     */
    private byte[] content;

    /**
     * Set the content of the report.
     * 
     * @param content the report content.
     */
    public void setContent(byte[] content) {
        this.content = content;
    }

    /**
     * {@inheritDoc}
     */
    public InputStream getInputStream() throws CWException {
        return new ByteArrayInputStream(content);
    }

    /**
     * {@inheritDoc}
     */
    public String getName() {
        return "name";
    }

    /**
     * {@inheritDoc}
     */
    public String getMimeType() {
        return OPTIMIZATION_REPORT_MIMETYPE;
    }

    /**
     * {@inheritDoc}
     */
    public String getReportType() {
        return OPTIMIZATION_REPORT_TYPE;
    }

    /**
     * {@inheritDoc}
     */
    public long getSize() {
        return content.length;
    }

    /**
     * {@inheritDoc}
     */
    public boolean isAvailable() {
        return true;
    }

    /**
     * Unsupported method. There is no id for optimization reports, they are generated on-demand.
     * <p>
     * {@inheritDoc}
     */
    public String getId() {
        throw new CWRuntimeException("XSLTOptimizationReport::getId() not supported");
    }

    /**
     * Unsupported method. There is no modified date for optimization reports, they are generated on-demand.
     * <p>
     * {@inheritDoc}
     */
    public DateTime getLastModified() {
        throw new CWRuntimeException("XSLTOptimizationReport::getLastModified() not supported");
    }

    /**
     * Unsupported method. It's not possible to change the mime type of a optimization report.
     * <p>
     * {@inheritDoc}
     */
    public void setMimeType(String arg0) {
        throw new CWRuntimeException("XSLTOptimizationReport::setMimeType() not supported");
    }

	@Override
	public ReportAccessLevel getAccessLevel() {
		// TODO Auto-generated method stub
		return null;
	}
}
