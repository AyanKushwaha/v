package com.sas.interbids.requests;

import com.jeppesen.carmen.crewweb.interbids.bo.RequestLogEntry;
import com.jeppesen.carmen.crewweb.interbids.customization.api.CancelableContext;
import com.jeppesen.carmen.crewweb.interbids.customization.api.RequestLogCancelableStrategy;

/**
 * Reference implementation.
 */
public class DefaultCancelableStrategy implements RequestLogCancelableStrategy {

    static final String[] STATUSES_THAT_IMPLIES_CANCELABILITY = {"rejected", "error"};

    @Override
    public boolean isCancelable(RequestLogEntry entry, CancelableContext context) {
        boolean cancelable = false;
        String status = entry.getStatus();
       for(String s : STATUSES_THAT_IMPLIES_CANCELABILITY){
           if(s.equals(status)){
                   cancelable = true;
           }
       }
       return cancelable;
    }

}