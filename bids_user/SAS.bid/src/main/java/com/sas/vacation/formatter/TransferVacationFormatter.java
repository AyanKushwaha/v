package com.sas.vacation.formatter;

import com.jeppesen.carmen.crewweb.jmpframework.customization.api.Bid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidDetailsFormatter;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.FormatterContext;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationAware;
import com.sas.vacation.base.BaseFormatter;

public class TransferVacationFormatter extends BaseFormatter implements BidDetailsFormatter, LocalizationAware {

    @Override
    public String formatDetails(Bid bid, FormatterContext formatterContext) {
        StringBuffer buff = new StringBuffer();

        appendNumberOfDays(buff, bid, "transfer_vacation");
        
        return buff.toString();
    }

}
