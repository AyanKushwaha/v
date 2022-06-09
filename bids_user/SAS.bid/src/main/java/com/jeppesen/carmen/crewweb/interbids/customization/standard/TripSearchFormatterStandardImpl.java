package com.jeppesen.carmen.crewweb.interbids.customization.standard;

import java.util.Collection;
import java.util.List;

import com.jeppesen.carmen.crewweb.interbids.bo.BidProperty;
import com.jeppesen.carmen.crewweb.interbids.bo.BidPropertyEntry;
import com.jeppesen.carmen.crewweb.interbids.bo.TripSearch;
import com.jeppesen.carmen.crewweb.interbids.customization.TripSearchFormatter;

/**
 * Used to format details for trip searches.
 */
public class TripSearchFormatterStandardImpl implements TripSearchFormatter {

    /**
     * {@inheritDoc}
     */
    public String format(TripSearch tripSearch) {

        StringBuilder result = new StringBuilder();

        List<BidProperty> bidProperties = tripSearch.getBidProperties();
        for (BidProperty bidProperty : bidProperties) {
            result.append(" [");
            result.append(bidProperty.getType());

            Collection<BidPropertyEntry> bidPropertyEntries = bidProperty.getBidPropertyEntries();
            for (BidPropertyEntry bidPropertyEntry : bidPropertyEntries) {
                result.append(" {");
                result.append(bidPropertyEntry.getEntryKey());
                result.append("=");
                result.append(bidPropertyEntry.getEntryValue());
                result.append("}");
            }

            result.append("]");
        }
        return result.toString();
    }

    /**
     * {@inheritDoc}
     */
    public String formatAsReport(TripSearch tripSearch) {
        StringBuffer buf = new StringBuffer();
        buf.append("Search criteria for search named: ").append(tripSearch.getName()).append("<br/>");
        buf.append(format(tripSearch));
        return buf.toString();
     }
}
