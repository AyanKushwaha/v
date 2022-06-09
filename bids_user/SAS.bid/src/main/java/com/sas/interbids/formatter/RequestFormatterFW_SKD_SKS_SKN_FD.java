package com.sas.interbids.formatter;

import com.jeppesen.carmen.crewweb.interbids.bo.RequestLogEntry;
import com.jeppesen.carmen.crewweb.interbids.customization.api.RequestFormatterInterface;

public class RequestFormatterFW_SKD_SKS_SKN_FD extends Formatter implements RequestFormatterInterface {

    @Override
    public String formatDetails(RequestLogEntry requestLogEntry) {
        StringBuilder fw = new StringBuilder();
        String requestType = requestLogEntry.getType();
        append(fw, localize(requestType), " - ");

        String startDate = requestLogEntry.getPropertyValue("start");
        String endDate = requestLogEntry.getPropertyValue("end");
        appendRequestPeriodDateAndTime(fw, startDate, endDate);

        return fw.toString();
    }
}
