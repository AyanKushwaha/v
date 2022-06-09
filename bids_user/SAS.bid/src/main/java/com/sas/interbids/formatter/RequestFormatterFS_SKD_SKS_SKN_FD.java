package com.sas.interbids.formatter;

import com.jeppesen.carmen.crewweb.interbids.bo.RequestLogEntry;
import com.jeppesen.carmen.crewweb.interbids.customization.api.RequestFormatterInterface;

public class RequestFormatterFS_SKD_SKS_SKN_FD extends Formatter implements RequestFormatterInterface {

    @Override
    public String formatDetails(RequestLogEntry requestLogEntry) {
        StringBuilder s = new StringBuilder();
        String requestType = requestLogEntry.getType();
        append(s, localize(requestType), " - ");

        String startDate = requestLogEntry.getPropertyValue("start");
        String endDate = requestLogEntry.getPropertyValue("end");
        appendRequestPeriodDateAndTime(s, startDate, endDate);

        return s.toString();
    }
}
