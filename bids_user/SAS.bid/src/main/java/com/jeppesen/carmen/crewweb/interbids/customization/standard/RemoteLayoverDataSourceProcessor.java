package com.jeppesen.carmen.crewweb.interbids.customization.standard;

import java.io.Reader;
import java.util.HashMap;
import java.util.Vector;

import nu.xom.Builder;
import nu.xom.Document;
import nu.xom.Element;
import nu.xom.Elements;

import com.jeppesen.carmen.crewweb.backendfacade.backend.BackEndConnectionInterface;
import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceContainer;
import com.jeppesen.carmen.crewweb.backendfacade.bo.DataSourceDescriptor;
import com.jeppesen.carmen.crewweb.backendfacade.customization.SimpleDataSourceContainer;
import com.jeppesen.carmen.crewweb.backendfacade.customization.api.DataSourceProcessorInterface;
import com.jeppesen.carmen.crewweb.backendfacade.util.StringEncoderReader;
import com.jeppesen.carmen.crewweb.framework.context.aware.BackEndConnectionAware;
import com.jeppesen.jcms.crewweb.common.exception.CWException;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;

/**
 * This class contains the data source processor for the layover stations XML coming from Studio.
 */
public class RemoteLayoverDataSourceProcessor implements DataSourceProcessorInterface, BackEndConnectionAware {

    /**
     * The back-end connection interface.
     */
    private BackEndConnectionInterface backEndConnection;

    /**
     * {@inheritDoc}
     */
    public void setBackEndConnection(BackEndConnectionInterface backEndConnection) {
        this.backEndConnection = backEndConnection;
    }

    /**
     * Process the datasource content by requesting the data (XML) from the back-end server and then process it using
     * XOM.
     * <p>
     * <b>Example XML:</b>
     * 
     * <pre>
     * &lt;PBS&gt;
     * &lt;LAYOVERS&gt;
     * &lt;LAYOVER id=&quot;LGW&quot;  name=&quot;Gatwick&quot;/&gt;
     * &lt;LAYOVER id=&quot;LHR&quot;  name=&quot;Heathrow&quot;/&gt;
     * &lt;LAYOVER id=&quot;ABI&quot;  name=&quot;Muni&quot;/&gt;
     * &lt;LAYOVER id=&quot;NCL&quot;  name=&quot;Newcastle&quot;/&gt;
     * &lt;LAYOVER id=&quot;HAJ&quot;  name=&quot;Hanover&quot;/&gt;
     * &lt;LAYOVER id=&quot;GLA&quot;  name=&quot;Glasgow Arpt&quot;/&gt;
     * &lt;LAYOVER id=&quot;GVA&quot;  name=&quot;Geneva&quot;/&gt;
     * &lt;LAYOVER id=&quot;ABZ&quot;  name=&quot;Aberdeen&quot;/&gt;
     * &lt;LAYOVER id=&quot;JER&quot;  name=&quot;Jersey&quot;/&gt;
     * &lt;LAYOVER id=&quot;EDI&quot;  name=&quot;Edinburgh&quot;/&gt;
     * &lt;/LAYOVERS&gt;
     * &lt;/PBS&gt;
     * </pre>
     * 
     * @param descriptor the data source processor.
     * @return the data source container with data.
     */
    public DataSourceContainer process(DataSourceDescriptor descriptor) {
        String xml = loadXML(descriptor);

        try {
            Reader reader = new StringEncoderReader(xml);
            Builder builder = new Builder();
            Document document = builder.build(reader);

            Element rootElement = document.getRootElement();
            Element layovers = rootElement.getFirstChildElement("LAYOVERS");
            Elements childElements = layovers.getChildElements();

            SimpleDataSourceContainer result = new SimpleDataSourceContainer();
            HashMap<String, Object> field = new HashMap<String, Object>();
            field.put("name", "value");
            result.addFieldMetaData(field);
            field = new HashMap<String, Object>();
            field.put("name", "name");
            result.addFieldMetaData(field);

            for (int i = 0; i < childElements.size(); i++) {
                Element element = childElements.get(i);
                HashMap<String, Object> data = new HashMap<String, Object>();
                data.put("value", element.getAttributeValue("id"));
                data.put("name", element.getAttributeValue("name"));
                result.addData(data);
            }

            return result;
        } catch (Exception e) {
            throw new CWRuntimeException("Unable to create datsource DOM tree for: " + descriptor.getName(), e);
        }
    }

    /**
     * Load the XML content.
     * 
     * @param descriptor the data source descriptor specifying which data source to load.
     * @return the file content as a string.
     */
    private String loadXML(DataSourceDescriptor descriptor) {
        String name = descriptor.getName();
        String prefix = descriptor.getPrefix();
        String methodName = "get_" + name.substring(prefix.length() + 1);

        try {
            return (String) backEndConnection.execute(null, new Vector<Object>());
        } catch (CWException e) {
            throw new CWRuntimeException("Unable to retrieve remote data source content! " + descriptor.getName(), e);
        }
    }

    public DataSourceContainer process(DataSourceDescriptor descriptor, java.util.Map<String, String> requestParams) {
	return null;
    }
}
