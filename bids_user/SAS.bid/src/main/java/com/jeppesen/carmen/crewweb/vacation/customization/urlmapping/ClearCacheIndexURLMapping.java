package com.jeppesen.carmen.crewweb.vacation.customization.urlmapping;

import com.jeppesen.carmen.crewweb.framework.business.TemplateContent;
import com.jeppesen.carmen.crewweb.jmpframework.context.CrewInformationContentManager;
import com.jeppesen.carmen.crewweb.vacation.context.VacationApplicationContextImpl;
import com.jeppesen.jcms.crewweb.common.configuration.CompressionMode;
import com.jeppesen.jcms.crewweb.common.configuration.ConfigurationManager.MessageLevel;
import com.jeppesen.jcms.crewweb.common.context.CWContext;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationManagerAware;
import com.jeppesen.jcms.crewweb.common.exception.CWException;
import com.jeppesen.jcms.crewweb.common.exception.CWRuntimeException;
import com.jeppesen.jcms.crewweb.common.localization.LocaleHelper;
import com.jeppesen.jcms.crewweb.common.localization.Localization;
import com.jeppesen.jcms.crewweb.common.localization.LocalizationManager;
import com.jeppesen.jcms.crewweb.common.service.AbstractNoCacheURLMapping;
import com.jeppesen.jcms.crewweb.common.util.CWLog;
import org.apache.commons.lang.StringUtils;
import org.apache.struts2.json.DefaultJSONWriter;
import org.apache.struts2.json.JSONException;
import org.apache.struts2.json.JSONUtil;

import javax.servlet.ServletContext;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.*;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import static com.jeppesen.jcms.crewweb.common.constants.CommonConstants.EXTJS_MODULE;

/**
 * This class is used to render the main page of the module.
 */
public class ClearCacheIndexURLMapping extends AbstractNoCacheURLMapping implements LocalizationManagerAware {

    private static final JSONUtil jsonUtil = new JSONUtil();

    static {
        jsonUtil.setWriter(new DefaultJSONWriter());
    }

    /**
     * The logger for this class.
     */
    private static final CWLog LOG = CWLog.getLogger(com.jeppesen.carmen.crewweb.vacation.customization.urlmapping.ClearCacheIndexURLMapping.class);
    private LocalizationManager localizationManager;
    private CrewInformationContentManager crewInformationContentManager;

    /**
     * Default constructor using "pull".
     */
    public ClearCacheIndexURLMapping() {
        crewInformationContentManager = VacationApplicationContextImpl.getInstance().getCrewInformationContentManager();
    }

    /**
     * {@inheritDoc}
     */
    @Override
    protected String contextualErrorMessage() {
        return "Unable to render the main page";
    }

    /**
     * {@inheritDoc}
     */
    @Override
    protected void doProcess(HttpServletRequest request, HttpServletResponse response, ServletContext context)
            throws Throwable {
        PrintWriter writer = response.getWriter();
        try {
            CWContext.getContext();
            renderMainPage(writer, request);
        } catch (CWRuntimeException e) {
            LOG.error("Error occured rendering vacation main page.", e);
            request.getSession().invalidate();
            renderUnrestrictedPage(writer);
        }
        writer.flush();
    }

    /**
     * Render unauthorized page.
     *
     * @param writer used to render the page.
     */
    private void renderUnrestrictedPage(PrintWriter writer) {
        writer.write("{error:\"Unauthorized - you might've been logged out.\"}");
    }

    /**
     * Render the vacation main page.
     *
     * @param writer the response writer.
     * @param request the request.
     * @throws IOException if an IOException occur.
     * @throws CWException if a CWException occur.
     */
    private void renderMainPage(PrintWriter writer, HttpServletRequest request) throws IOException, CWException {
        StringBuilder sb = new StringBuilder();

        sb.append("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" "
                + "\"http://www.w3.org/TR/html4/loose.dtd\">");

        sb.append("<html>");
        sb.append("<head>\n");
        sb.append("<meta http-equiv='cache-control' content='no-cache'>\n");
        sb.append("<meta http-equiv='expires' content='0'>\n");
        sb.append("<meta http-equiv='pragma' content='no-cache'>\n");
        addCssLinkTags(request, sb);

        // TODO: flush output stream here, and possibly append blank space up to 2500 bytes?
        // TODO: use lab.js to load javascripts

        sb.append("</head>");
        sb.append("<body class='cw-application-body'>");

        addPageStructureTags(sb);

        inlineClientLocalizationMessages(sb);
        // Add ExtJS
        appendJavaScripts(sb);
        appendSharedJavaScriptModule("src/locale/ext-lang-" + new LocaleHelper(VacationApplicationContextImpl
                .getInstance()).getExtLocaleDef() + ".js", EXTJS_MODULE, sb);
        inlineUserInformation(sb);
        sb.append("<script>Ext.EventManager.onDocumentReady(js.vacation.Vacation.init, js.vacation.Vacation, true);</script>");
        sb.append("</body>");
        sb.append("</html>");
        String result = sb.toString();
        writer.write(result);
    }

    /**
     * Appends java scripts to sb.
     *
     * @param sb string buffer
     */
    private void appendJavaScripts(StringBuilder sb) {
        appendJavaScriptBasePathConstant(sb);

        CompressionMode compressionMode = getJavaScriptCompressionMode();
        switch (compressionMode) {
            case EXPLODED:
                appendSharedJavaScriptModule("adapter/ext/ext-base-debug.js", EXTJS_MODULE, sb);
                appendSharedJavaScriptModule("ext-all-debug.js", EXTJS_MODULE, sb);
                appendSharedJavaScriptResources(sb, "warp-jsbase-javascripts-all", "warp");
                appendSharedJavaScriptResources(sb, "warp-biddialog-javascripts", "warp");
                appendSharedJavaScriptResources(sb, "warp-jmp-javascripts", "warp");
                appendJavaScriptResources(sb, "vacation-javascripts");
                break;
            case DEBUG:
                appendSharedJavaScriptModule("adapter/ext/ext-base-debug.js", EXTJS_MODULE,sb);
                appendSharedJavaScriptModule("ext-all-debug.js", EXTJS_MODULE, sb);
                appendSharedJavaScriptModule("js/warp-jsbase-all-debug.js", "warp", sb);
                appendSharedJavaScriptModule("js/warp-biddialog-all-debug.js", "warp", sb);
                appendSharedJavaScriptModule("js/warp-jmp-all-debug.js", "warp", sb);
                appendJavaScript("js/vac-all-debug.js", sb);
                break;
            case COMPRESSED:
                appendSharedJavaScriptModule("adapter/ext/ext-base.js", EXTJS_MODULE,sb);
                appendSharedJavaScriptModule("ext-all.js", EXTJS_MODULE, sb);
                appendSharedJavaScriptModule("js/warp-jsbase-all.js", "warp", sb);
                appendSharedJavaScriptModule("js/warp-biddialog-all.js", "warp", sb);
                appendSharedJavaScriptModule("js/warp-jmp-all.js", "warp", sb);
                appendJavaScript("js/vac-all.js", sb);
                break;
            default:
                throw new CWRuntimeException("Unrecognized javascript compression mode");
        }

        appendImplementationJavascripts(sb, "vacation-widget-file");
        appendImplementationJavascripts(sb, "vacation-js-implementation");
    }

    /**
     * Adds CSS style sheet links to sb.
     *
     * @param request the http request
     * @param sb the string buffer
     */
    private void addCssLinkTags(HttpServletRequest request, StringBuilder sb) {
        appendSharedStyleSheetModule("resources/css/ext-all.css", EXTJS_MODULE, sb);

        CompressionMode compressionMode = getStyleSheetCompressionMode();
        switch (compressionMode) {
            case EXPLODED:
                appendSharedStyleSheetResources(sb, "warp-jsbase-stylesheets", "warp");
                appendSharedStyleSheetResources(sb, "warp-biddialog-stylesheets", "warp");
                appendSharedStyleSheetResources(sb, "warp-jmp-stylesheets", "warp");
                appendStyleSheetResources(sb, "vacation-stylesheets");
                break;
            case DEBUG:
                appendSharedStyleSheetModule("css/warp-jsbase-all-debug.css", "warp", sb);
                appendSharedStyleSheetModule("css/warp-biddialog-all-debug.css", "warp", sb);
                appendSharedStyleSheetModule("css/warp-jmp-all-debug.css", "warp", sb);
                appendStyleSheet("css/vac-all-debug.css", sb);
                break;
            case COMPRESSED:
                appendSharedStyleSheetModule("css/warp-jsbase-all.css", "warp", sb);
                appendSharedStyleSheetModule("css/warp-biddialog-all.css", "warp", sb);
                appendSharedStyleSheetModule("css/warp-jmp-all.css", "warp", sb);
                appendStyleSheet("css/vac-all.css", sb);
                break;
            default:
                throw new CWRuntimeException("Unrecognized javascript compression mode");
        }

        appendStyleSheet("css/generated.css", sb);
        appendStyleSheet("css/implementation.css", sb);
    }

    /**
     * Adds the page's HTML skeleton.
     *
     * @param sb string buffer
     */
    private void addPageStructureTags(StringBuilder sb) {
        sb.append("<pre> </pre>");
        sb.append("<div id='vacation_viewport'>");
        sb.append("<div id='vacation_viewport'>");
        sb.append("<div id='vacation_loading'>");
        String message = translate("loading_application"); // TODO: html char escape
        sb.append("<img src='img/wait.gif' height='18' width='18' alt='" + message + "' align='absmiddle' />");
        sb.append(message + "</div>");
        sb.append("</div>");
    }

    /**
     * We inline the localization messages since they are used when showing the splash screen.
     *
     * @param sb the string builder
     */
    private void inlineClientLocalizationMessages(StringBuilder sb) {
        sb.append("\n<script id='vacation_localization_id'>");
        sb.append("var vacation_localization_id=");
        Map<String, String> map = new HashMap<>();
        map.put("appl.name", translate("application.name"));
        map.put("appl.version", translate("application.version"));

        Localization localization = localizationManager.getClientLocalization();
        Set<String> sStr = localization.getKeys();
        for (String string : sStr) {
            map.put(string, localization.MSGR(string));
        }
        String mapAsJson = "";
        try {
            mapAsJson = jsonUtil.serialize(map, false);
        } catch (JSONException e) {
            LOG.warn("Failed to send inlined localization strings to client", e);
        }
        sb.append(mapAsJson);
        sb.append("</script>");
    }

    protected void inlineUserInformation(StringBuilder sb) {
        TemplateContent detailedCrewInfoTemplateContent = crewInformationContentManager.getDetailedCrewInfoTemplate("vacation");
        String simpleCrewInfoTemplate = escapeTemplate(crewInformationContentManager.getSimpleCrewInfoTemplate("vacation"));
        sb.append("\n<script id='user_information_id'>");
        sb.append("function getCrewInformationTemplates(){ return { simpleTemplate: \"" + simpleCrewInfoTemplate + "\"");
        if (detailedCrewInfoTemplateContent != null) {
            String detailedCrewInfoTemplate = escapeTemplate(detailedCrewInfoTemplateContent);
            sb.append(", detailedTemplate:\"" + detailedCrewInfoTemplate + "\"");
        }
        sb.append("};}");
        sb.append("</script>");

    }

    private String escapeTemplate(TemplateContent template) {
        String originalOutput = template.getOutput();
        if (StringUtils.isNotEmpty(originalOutput)) {
            String singleLine = originalOutput.replaceAll("[\n\r\t]", "");
            String singleLineEscaped = singleLine.replace("\"", "\\\"");

            return singleLineEscaped;
        }
        return null;
    }

    /**
     * Returns the l10n string for the specified key.
     *
     * @param translationKey the key
     * @return the l10n string for the key
     */
    private String translate(String translationKey) {
        return localizationManager.getServerLocalization().MSGR(translationKey);
    }

    public void setLocalizationManager(LocalizationManager localizationManager) {
        this.localizationManager = localizationManager;
    }

    // TODO: attach a SCRIPT tag after the application has started, like js.pack.onReady(...)
    /**
     * Appends java script resource that isn't needed when the application is started.
     *
     * @param javascript the script resource
     * @param sb the string builder
     */

    /**
     * Append customization widgets.
     * <p>
     * Done in a separate method from appendResources(String, StringBuilder, String) due to the fact that if
     * the file does not exist we want to warn the user that they may have forgotten to include this file.
     * </p>
     *
     * @param sb - string buffer
     */
    private void appendImplementationJavascripts(StringBuilder sb, String fileName) {
        try {
            String appendingFilePath = "js/";
            String widgetFileName = configurationManager.getPropertyAsString("vacation."+fileName,
                    MessageLevel.WARNING_MESSAGE);
            if (widgetFileName == null || widgetFileName.length() < 1) {
                widgetFileName = fileName.equals("widget-file") ? "vacation-widget" : fileName;
            }
            InputStream is = resourceLocator.getResourceAsStream(widgetFileName);
            if (is != null) {
                BufferedReader bf = new BufferedReader(new InputStreamReader(is));
                for (String js = bf.readLine(); js != null; js = bf.readLine()) {
                    js = js.trim();
                    if (js.length() < 1 || js.startsWith("#") || js.startsWith("//")) {
                        continue;
                    }
                    if (!js.endsWith(".js")) {
                        js += ".js";
                    }
                    js = appendingFilePath.concat(js);
                    appendImplementationJavaScriptWithVersioning(js, sb);
                }
                bf.close();
            }
        } catch (IOException e) {
            LOG.warn("no "+ fileName +" file definition found in src/main/resources. "
                    + "If you have custom javascript files please add them to the this file. ");
        }
    }

    private StringBuilder appendImplementationJavaScriptWithVersioning(String javascript, StringBuilder stringbuilder) {
        final String startTag = "<script type=\"text/javascript\" src=\"";
        final String endTag = "\"></script>\n";
        return stringbuilder.append(startTag).append(javascript).append(endTag);
    }

}

