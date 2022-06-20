package com.sas.career.formatter;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.net.URLConnection;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.joda.time.DateTime;

import com.jeppesen.carmen.crewweb.framework.business.facade.UserAPI;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.framework.reports.Report;
import com.jeppesen.carmen.crewweb.framework.reports.ReportAccessLevel;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.Bid;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.BidProperty;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.ImmutableBidGroup;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.ImmutablePeriod;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.PrintReceiptContext;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.PropertyEntry;
import com.jeppesen.carmen.crewweb.jmpframework.customization.api.ReceiptGenerator;
import com.jeppesen.jcms.crewweb.common.exception.CWException;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.jeppesen.jcms.crewweb.common.util.CWLog;

public class CareerBidReceipt extends Formatter implements ReceiptGenerator, UserCustomizationAPIAware {

	UserCustomizationAPI userCustomization;
	private static final CWLog LOG = CWLog.getLogger(CareerBidReceipt.class);
	
    @Override
    public Report generateReceiptReport(List<ImmutableBidGroup> bidGroups, PrintReceiptContext context) {

    	
    	StringBuffer buff = new StringBuffer();
    	CWDateTime currentDate = CWDateTime.create(System.currentTimeMillis());
    	
    	buff.append("<html>");
    	buff.append("<head>" + "<title>Receipt - ").append(currentDate.toString()).append("</title>");
    	buff.append("<link type=\"text/css\" rel=\"stylesheet\" href=\"css/implementation.css\">");
    	buff.append("<meta http-equiv=\"content-type\" content=\"text/html;charset=UTF-8\" />");
    	buff.append("</head>");
    	buff.append("<body id=\"bidGroupReceipt\">");
    	generateUserInfo(buff, context);
    	buff.append("<br>");
    	
    	buff.append("<table id=\"bidGroupReceiptTable\">");
    	generateHeader(buff);
    	
    	Collections.sort(bidGroups, new BidGroupComparator());
    	
    	int numPrevBids = 0;
    	for (ImmutableBidGroup immutableBidGroup : bidGroups) {
    		if (immutableBidGroup.getBids().size() > 0) {
    			List<Bid> bids = immutableBidGroup.getBids();
    			Collections.sort(bids, new CustomComparator());
    			generateBGReport(buff, bids, numPrevBids);
    			numPrevBids += bids.size();
    		}
    		
    	}
    	buff.append("</table>");
    	buff.append("</body>");
    	buff.append("</html>");
    	return new GeneratedReport(buff);
    	
    	/*
    	StringBuffer buff = new StringBuffer();
    	
    	for (ImmutableBidGroup immutableBidGroup : bidGroups) {
    		List<Bid> bids = immutableBidGroup.getBids();
//    		Collections.sort(bids, new CustomComparator());
    		
    		CWDateTime currentDate = CWDateTime.create(System.currentTimeMillis());
    		buff.append("<html>");
    		buff.append("<head>" + "<title>Receipt - ").append(currentDate.toString()).append("</title>");
    		buff.append("<link type=\"text/css\" rel=\"stylesheet\" href=\"css/implementation.css\">");
    		buff.append("<meta http-equiv=\"content-type\" content=\"text/html;charset=UTF-8\" />");
    		buff.append("</head>");
    		buff.append("<body id=\"bidGroupReceipt\">");
    		//        buff.append("<ul>");
    		generateUserInfo(buff, context);
    		buff.append("<br>");
    		
    		buff.append("<table id=\"bidGroupReceiptTable\">");
    		generateHeader(buff);
    		generateBGReport(buff, bids);
    		//        buff.append("</ul>");
    		buff.append("</table>");
    		buff.append("</body>");
    		buff.append("</html>");
    		
    	}
    	return new GeneratedReport(buff);
    	*/
    }
    
    private void generateUserInfo(StringBuffer sb, PrintReceiptContext context) {
    	UserAPI userAPI = userCustomization.getUserAPI(userCustomization.getUserId());
    	
    	String firstName = userAPI.getFirstName();
    	String lastName = userAPI.getLastName();
    	String userID = userAPI.getLoginId();
    	
    	sb.append("<table id=\"bidGroupReceiptUserInfo\">");
    	sb.append("<tr>");
    	sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">FDA period:</th>");
    	sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">Deadline:</th>");
    	sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">Employee no:</th>");
    	sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">Name:</th>");
//    	sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">Receipt generated at:</th>");
    	sb.append("</tr>");
    	
    	sb.append("<tr>");
    	
    	
    	ImmutablePeriod period = context.getPeriod();
    	CWDateTime periodStart = period.getPeriodFrom();
    	CWDateTime periodEnd = period.getPeriodTo();
    	CWDateTime windowEnd = period.getWindowTo();
//    	CWDateTime now = CWDateTime.create(new DateTime().getMillis());
    	
    	sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">" + formatDate(periodStart) + " - " + formatDate(periodEnd) + "</td>");
    	sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">" + formatDate(windowEnd) + "</td>");
    	sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">" + userID + "</td>");
    	sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">" + lastName + ", " + firstName + "</td>");
//    	sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">" + getDateTimeWithFormat(CWDateTime.formatISODateTime(now), "ddMMMyy HH:mm") + "</td>");
    	
    	sb.append("</tr>");
    	
    	sb.append("</table>");
    }
    
    private void generateHeader(StringBuffer sb) {
    	sb.append("<tr id=\"bidGroupReceiptTableHeader\">");
    	sb.append("<th id=\"bidGroupReceiptTableHeaderCell\"  width=\"100px\">Bid type</th>");
    	sb.append("<th id=\"bidGroupReceiptTableHeaderCell\" width=\"250px\">Details</th>");
    	sb.append("<th id=\"bidGroupReceiptTableHeaderCell\">Created</th>");
    	sb.append("<th id=\"bidGroupReceiptTableHeaderCell\">Updated</th>");
    	sb.append("</tr>");
    }
    

    private void generateBGReport(StringBuffer sb, List<Bid> allBids, int numPrevBids) {

    	for (int i = 0; i < allBids.size(); i++) {
    		Bid bid = allBids.get(i);
    		System.out.println("Bid type: " + bid.getType());
    		System.out.println("i+numPrevBids = " + (i+numPrevBids));
    		System.out.println("i+numPrevBids modulus = " + ((i+numPrevBids)%2));
    		if ((i+numPrevBids)%2 == 0) {
    			sb.append("<tr id=\"bidGroupReceiptTableBodyEven\">");
    		} else {
    			sb.append("<tr id=\"bidGroupReceiptTableBodyOdd\">");
    		}
    		generateBidType(sb, bid);
    		generateDetails(sb, bid);
    		generateCreatedDate(sb, bid);
    		generateUpdatedDate(sb, bid);
    		sb.append("</tr>");
    	}
    }
    
    private void generateBidType(StringBuffer sb, Bid bid) {
    	sb.append("<td id=\"bidGroupReceiptTableBodyCell\"  width=\"100px\">");
    	sb.append(format(bid.getType()));
    	sb.append("</td>");
    }
    
    private void generateDetails(StringBuffer sb, Bid bid) {
    	sb.append("<td id=\"bidGroupReceiptTableBodyCell\" width=\"250px\">");
    	
    	if (bid.getType().equalsIgnoreCase("BASE")) {
    		getBaseDetails(sb, bid);
    	} else if (bid.getType().equalsIgnoreCase("FBID")) {
    		getFBIDDetails(sb, bid);
    	} else if (bid.getType().equalsIgnoreCase("FCAC")) {
    		getFCACDetails(sb, bid);
    	} else if (bid.getType().equalsIgnoreCase("FOAC")) {
    		getFOACDetails(sb, bid);
    	} else if (bid.getType().equalsIgnoreCase("CCAC")) {
    		getCCACDetails(sb, bid);
    	} else if (bid.getType().equalsIgnoreCase("NORTHNORWAY")) {
    		getNorthNorwayDetails(sb, bid);
    	} else if (bid.getType().equalsIgnoreCase("ATPL")) {
    		getATPLConfirmationDetails(sb, bid);
    	}
    	sb.append("</td>");
    }
    
    private void getBaseDetails(StringBuffer sb, Bid bid) {
    	try {
			sb.append(format(BaseTypeFormatter.BASE_TRANSLATION_KEY, formatValuesetValue(getBidPropertyValue(bid, BaseTypeFormatter.KEY))));
		} catch (CWException e) {
			sb.append(format("value_not_found"));
		}
    }
    
    private void getFBIDDetails(StringBuffer sb, Bid bid) {
    	try {
    		// Removed until UICMP-3047 is fixed
//        	sb.append(format(PRIORITY_TRANSLATION_KEY, bid.getPrio()));
    		sb.append(format(FBIDTypeFormatter.QUAL_TRANSLATION_KEY, formatValuesetValue(getBidPropertyValue(bid, FBIDTypeFormatter.KEY))));
    	} catch (Exception e) {
    		LOG.error(e.getMessage());
    		
    		sb.append(format(BID_VALUE_NOT_FOUND));
    	}
    }
    
    private void getFCACDetails(StringBuffer sb, Bid bid) {
    	try {
    		// Removed until UICMP-3047 is fixed
//        	sb.append(format(PRIORITY_TRANSLATION_KEY, bid.getPrio()));
    		sb.append(format(FCACTypeFormatter.QUAL_TRANSLATION_KEY, formatValuesetValue(getBidPropertyValue(bid, FCACTypeFormatter.KEY))));
    	} catch (Exception e) {
    		LOG.error(e.getMessage());
    		
    		sb.append(format(BID_VALUE_NOT_FOUND));
    	}
    }
    
    private void getFOACDetails(StringBuffer sb, Bid bid) {
    	try {
    		// Removed until UICMP-3047 is fixed
//        	sb.append(format(PRIORITY_TRANSLATION_KEY, bid.getPrio()));
    		sb.append(format(FOACTypeFormatter.QUAL_TRANSLATION_KEY, formatValuesetValue(getBidPropertyValue(bid, FOACTypeFormatter.KEY))));
    	} catch (Exception e) {
    		LOG.error(e.getMessage());
    		
    		sb.append(format(BID_VALUE_NOT_FOUND));
    	}
    }
    
    private void getCCACDetails(StringBuffer sb, Bid bid) {
    	try {
    		// Removed until UICMP-3047 is fixed
//        	sb.append(format(PRIORITY_TRANSLATION_KEY, bid.getPrio()));
    		sb.append(format(CCACTypeFormatter.QUAL_TRANSLATION_KEY, formatValuesetValue(getBidPropertyValue(bid, CCACTypeFormatter.KEY))));
    	} catch (Exception e) {
    		LOG.error(e.getMessage());
    		
    		sb.append(format(BID_VALUE_NOT_FOUND));
    	}
    }
    
    private void getNorthNorwayDetails(StringBuffer sb, Bid bid) {
		sb.append(format("north_norway_details_formatter"));
	}
    
    private void getATPLConfirmationDetails(StringBuffer sb, Bid bid) {
		sb.append(format("atpl_confirmation_details_formatter"));
	}
    
    private String getBidPropertyValue(Bid bid, String propertyName) throws CWException {
    	for (BidProperty property : bid.getProperties()) {
    		for (PropertyEntry entry : property.getPropertyEntries()) {
    			if (entry.getName().equalsIgnoreCase(propertyName)) {
    				return entry.getValue();
    			}
    				
    		}
    	}
    	throw new CWException("No value for property " + propertyName + "found");
    }
    

	private void generateCreatedDate(StringBuffer sb, Bid bid) {
    	sb.append("<td id=\"bidGroupReceiptTableBodyCell\">");
    	String created = bid.getCreated();
    	if (created != null && !created.equalsIgnoreCase("")) {
    		sb.append(getDateTimeWithFormat(bid.getCreated(), "ddMMMyy HH:mm"));
    	} else {
    		sb.append(format("creation_not_available"));
    	}
    	sb.append("</td>");
    }
    
    private void generateUpdatedDate(StringBuffer sb, Bid bid) {
    	sb.append("<td id=\"bidGroupReceiptTableBodyCell\">");
    	String updated = bid.getUpdated();
    	if (updated != null && !updated.equalsIgnoreCase("")) {
    		sb.append(getDateTimeWithFormat(bid.getUpdated(), "ddMMMyy HH:mm"));
    	} else {
    		sb.append(format("update_not_available"));
//    		sb.append("<br>");
    	}
    	sb.append("</td>");
    }
    

    static class GeneratedReport implements Report {
        /** Buffer. */
        private byte[] buffer = null;
        /** created time. */
        private Date createdTime = null;
        /** mime type. */
        private String mimeType = null;

        /**
         * Constructor .
         * 
         * @param buffer
         *            the buffer.
         */
        GeneratedReport(StringBuffer buffer) {
            this.buffer = buffer.toString().getBytes();
            createdTime = new Date();
        }

        /** {@inheritDoc} */
        public String getId() {
            return "Generated Receipt " + createdTime;
        }

        /** {@inheritDoc} */
        public InputStream getInputStream() throws CWException {
            return new ByteArrayInputStream(buffer);
        }

        /** {@inheritDoc} */
        public DateTime getLastModified() {
            return new DateTime(createdTime.getTime());
        }

        /** {@inheritDoc} */
        public String getMimeType() {
            if (mimeType == null) {
                mimeType = URLConnection.getFileNameMap().getContentTypeFor(getName());
            }
            return mimeType;
        }

        /** {@inheritDoc} */
        public String getName() {
            return "Receipt.html";
        }

        /** {@inheritDoc} */
        public String getReportType() {
            String s = getMimeType();
            if (s == null) {
                return null;
            }
            s = s.trim();
            int ix = s.lastIndexOf('/');
            while (ix == s.length() - 1) {
                s = s.substring(0, ix);
                ix = s.lastIndexOf('/');
            }
            return s.substring(ix + 1);
        }

        /** {@inheritDoc} */
        public long getSize() {
            return buffer.length;
        }

        /** {@inheritDoc} */
        public boolean isAvailable() {
            return true;
        }

        /** {@inheritDoc} */
        public void setMimeType(String type) {
            mimeType = type;
        }

		@Override
		public ReportAccessLevel getAccessLevel() {
			// TODO Auto-generated method stub
			return null;
		}
    }
    
    private String formatDate(CWDateTime dateTime) {
    	try {
    		return getDateTimeWithFormat(CWDateTime.formatISODateTime(dateTime), "ddMMMyy");
		} catch (Exception e) {
			return "N/A";
		}
    }
    
    @Override
    public void setUserCustomizationAPI(UserCustomizationAPI arg0) {
    	this.userCustomization = arg0;
    }
    
    public class CustomComparator implements Comparator<Bid> {
        @Override
        public int compare(Bid o1, Bid o2) {
        	
        	String o1_string = o1.getType() + "_" + o1.getPrio();
        	String o2_string = o2.getType() + "_" + o2.getPrio();
        	return o1_string.compareTo(o2_string);
        }
    }
    
    public class BidGroupComparator implements Comparator<ImmutableBidGroup> {
    	
    	private Map<String, Integer> groupOrder = new HashMap<String, Integer>();
    	
    	public BidGroupComparator() {
    		groupOrder.put("transition_fcac", 1);
    		groupOrder.put("transition_foac", 2);
    		groupOrder.put("transition_base", 3);
    		groupOrder.put("transition_atpl", 4);
    		groupOrder.put("transition_nn", 5);
		}

		@Override
		public int compare(ImmutableBidGroup o1, ImmutableBidGroup o2) {
			if(!groupOrder.containsKey(o1.getId().toLowerCase())) {
				return 1;
			} else if (!groupOrder.containsKey(o2.getId().toLowerCase())) {
				return -1;
			}
			
			int o1_order = groupOrder.get(o1.getId().toLowerCase());
			int o2_order = groupOrder.get(o2.getId().toLowerCase());
			
			return o1_order < o2_order ? -1 : 1;
		}
    	
    	
    }
    
    public class BidComparator implements Comparator<Bid> {

		@Override
		public int compare(Bid o1, Bid o2) {
			return o1.getPrio() < o2.getPrio() ? -1 : 1;
		}
    	
    }
}
