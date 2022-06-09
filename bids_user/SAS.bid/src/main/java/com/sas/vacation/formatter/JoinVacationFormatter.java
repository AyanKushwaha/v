package com.sas.vacation.formatter;

import java.util.List;

import com.jeppesen.carmen.crewweb.jmpframework.customization.api.Bid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidDetailsFormatter;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidProperty;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.FormatterContext;
import com.jeppesen.jcms.crewweb.common.context.aware.LocalizationAware;
import com.sas.vacation.base.BaseFormatter;

public class JoinVacationFormatter extends BaseFormatter implements BidDetailsFormatter, LocalizationAware {

    @Override
    public String formatDetails(Bid bid, FormatterContext formatterContext) {
        StringBuffer buff = new StringBuffer();
        List<BidProperty> properties = bid.getProperties();
        appendAlternative(properties, buff, 0);
        appendAlternative(properties, buff, 1);
        appendAlternative(properties, buff, 2);
        appendComment(buff, bid);
        
        return buff.toString();
    }

}
