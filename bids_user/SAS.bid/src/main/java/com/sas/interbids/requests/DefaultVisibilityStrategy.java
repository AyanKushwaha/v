package com.sas.interbids.requests;

import com.jeppesen.carmen.crewweb.interbids.bo.RequestLogEntry;
import com.jeppesen.carmen.crewweb.interbids.customization.api.RequestLogVisibilityStrategy;
import com.jeppesen.carmen.crewweb.interbids.customization.api.VisibilityContext;

/**
 * Reference implementation.
 */
public class DefaultVisibilityStrategy implements RequestLogVisibilityStrategy {

    static final String STATUS_WHICH_IMPLIES_INVISIBLE = "cancelled";

    @Override
    public boolean isVisible(RequestLogEntry entry, VisibilityContext context) {
        String status = entry.getStatus();
        if (STATUS_WHICH_IMPLIES_INVISIBLE.equals(status)) {
            return false;
        }
        return true;
    }

}