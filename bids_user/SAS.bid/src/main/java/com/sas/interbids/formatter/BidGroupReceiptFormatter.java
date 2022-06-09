package com.sas.interbids.formatter;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.URLConnection;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.List;

import org.joda.time.DateTime;

import com.jeppesen.carmen.crewweb.framework.bo.Period;
import com.jeppesen.carmen.crewweb.framework.business.DataSourceLookupHelper;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserAPI;
import com.jeppesen.carmen.crewweb.framework.business.facade.UserCustomizationAPI;
import com.jeppesen.carmen.crewweb.framework.context.aware.DataSourceLookupHelperAware;
import com.jeppesen.carmen.crewweb.framework.context.aware.UserCustomizationAPIAware;
import com.jeppesen.carmen.crewweb.framework.reports.Report;
import com.jeppesen.carmen.crewweb.framework.reports.ReportAccessLevel;
import com.jeppesen.carmen.crewweb.interbids.bo.Bid;
import com.jeppesen.carmen.crewweb.interbids.bo.BidGroup;
import com.jeppesen.carmen.crewweb.interbids.bo.BidProperty;
import com.jeppesen.carmen.crewweb.interbids.bo.BidPropertyEntry;
import com.jeppesen.carmen.crewweb.interbids.presentation.BidGroupReceiptGenerator;
import com.jeppesen.jcms.crewweb.common.exception.CWException;
import com.jeppesen.jcms.crewweb.common.util.CWDateTime;
import com.jeppesen.jcms.crewweb.common.util.CWLog;
import com.sas.interbids.base.SasConstants;
import com.sas.interbids.formatter.helper.PriorityStringLookupHelper;

/**
 * Default implementation of a BidGroup receipt generator.
 */
public class BidGroupReceiptFormatter extends Formatter implements
		BidGroupReceiptGenerator, UserCustomizationAPIAware,
		DataSourceLookupHelperAware {

	UserCustomizationAPI userCustomization;
	private static final CWDateTime UFN_DATE = CWDateTime
			.parseISODateTime("2035-12-31 23:59");
	private static final CWLog LOG = CWLog
			.getLogger(BidGroupReceiptFormatter.class);
	private DataSourceLookupHelper dataSourceLookupHelper;

	/**
	 * {@inheritDoc}
	 */
	public Report generateReport(List<BidGroup> bgList, boolean submittedOnly) {
		CWDateTime currentDate = CWDateTime.create(System.currentTimeMillis());
		StringBuffer buff = new StringBuffer();
		buff.append("<html>");
		buff.append("<head>" + "<title>Receipt - ")
				.append(currentDate.toString()).append("</title>");
		buff.append("<link type=\"text/css\" rel=\"stylesheet\" href=\"css/implementation.css\">");
		buff.append("<meta http-equiv=\"content-type\" content=\"text/html;charset=UTF-8\" />");
		buff.append("</head>");
		buff.append("<body id=\"bidGroupReceipt\">");
		generateUserInfo(buff);
		buff.append("<br>");

		buff.append("<table id=\"bidGroupReceiptTable\">");

		for (BidGroup bg : bgList) {
			if (submittedOnly && bg.getSubmitted() == null) { // Not submitted
				continue;
			}
			generateHeader(buff,
					bg.getName()
							.equals(SasConstants.BID_GROUP_NAME_PREFERENCES));
			generateBGReport(buff, bg,
					bg.getName()
							.equals(SasConstants.BID_GROUP_NAME_PREFERENCES));
		}
		buff.append("</table>");
		buff.append("</body>");
		buff.append("</html>");
		return new GeneratedReport(buff);
	}

	private void generateUserInfo(StringBuffer sb) {
		Period currentPeriodForUser = userCustomization
				.getCurrentPeriodForUser(userCustomization.getUserId(),
						SasConstants.PBS_PERIOD);
		UserAPI userAPI = userCustomization.getUserAPI(userCustomization
				.getUserId());

		String firstName = userAPI.getFirstName();
		String lastName = userAPI.getLastName();
		String userID = userAPI.getLoginId();

		sb.append("<table id=\"bidGroupReceiptUserInfo\">");
		sb.append("<tr>");
		sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">Rostering period:</th>");
		sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">Deadline:</th>");
		sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">Employee no:</th>");
		sb.append("<th id=\"bidGroupReceiptUserInfoHeaderCell\">Name:</th>");
		sb.append("</tr>");

		sb.append("<tr>");

		sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">");
		sb.append(formatDate(
				CWDateTime.formatISODate(currentPeriodForUser.getStart()),
				SasConstants.dateFormat));
		sb.append(" - ");
		sb.append(formatDate(
				CWDateTime.formatISODate(currentPeriodForUser.getEnd()),
				SasConstants.dateFormat));
		sb.append("</td>");

		sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">"
				+ formatDate(CWDateTime.formatISODate(currentPeriodForUser
						.getClose()), SasConstants.dateFormat) + "</td>");
		sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">" + userID
				+ "</td>");
		sb.append("<td id=\"bidGroupReceiptUserInfoBodyCell\">" + lastName
				+ ", " + firstName + "</td>");

		sb.append("</tr>");

		sb.append("</table>");
	}

	private void generateHeader(StringBuffer sb, boolean isPreferences) {
		sb.append("<tr id=\"bidGroupReceiptTableHeader\">");
		sb.append("<th id=\"bidGroupReceiptTableHeaderCell\"  width=\"100px\">Bid type</th>");
		sb.append("<th id=\"bidGroupReceiptTableHeaderCell\" width=\"250px\">Details</th>");
		sb.append("<th id=\"bidGroupReceiptTableHeaderCell\" width=\"170px\">Bid validity period</th>");
		if (!isPreferences) {
			sb.append("<th id=\"bidGroupReceiptTableHeaderCell\">Priority</th>");
		}
		sb.append("<th id=\"bidGroupReceiptTableHeaderCell\">Created</th>");
		sb.append("<th id=\"bidGroupReceiptTableHeaderCell\">Updated</th>");
		sb.append("</tr>");
	}

	private void generateBGReport(StringBuffer sb, BidGroup bg,
			boolean isPreferences) {
		List<Bid> allBids = bg.getAllBids();

		Collections.sort(allBids, new customComparator());

		for (int i = 0; i < allBids.size(); i++) {
			Bid bid = allBids.get(i);
			if (i % 2 == 0) {
				sb.append("<tr id=\"bidGroupReceiptTableBodyEven\">");
			} else {
				sb.append("<tr id=\"bidGroupReceiptTableBodyOdd\">");
			}
			generateBidType(sb, bid);
			generateDetails(sb, bid);
			generateBidValidityPeriod(sb, bid);
			if (!isPreferences) {
				generateBidPoints(sb, bid);
			}
			generateCreatedDate(sb, bid);
			generateUpdatedDate(sb, bid);
			sb.append("</tr>");
		}
	}

	private void generateBidType(StringBuffer sb, Bid bid) {
		sb.append("<td id=\"bidGroupReceiptTableBodyCell\"  width=\"100px\">");
		sb.append(localize("short_" + bid.getType()));
		sb.append("</td>");
	}

	private void generateDetails(StringBuffer sb, Bid bid) {
		sb.append("<td id=\"bidGroupReceiptTableBodyCell\" width=\"250px\">");
		sb.append(bid.getBidDetails());
		sb.append("</td>");
	}

	private void generateBidValidityPeriod(StringBuffer sb, Bid bid) {
		sb.append("<td id=\"bidGroupReceiptTableBodyCell\"  width=\"170px\">");
		sb.append(formatDateTime(
				CWDateTime.formatISODateTime(bid.getStartDate()),
				SasConstants.dateTimeFormat));

		if (bid.getEndDate() != null) {

			sb.append(" - ");
			if (bid.getEndDate().isEqual(UFN_DATE)) {
				sb.append("UFN");
			} else {
				sb.append(formatDateTime(
						CWDateTime.formatISODateTime(bid.getEndDate()),
						SasConstants.dateTimeFormat));
			}
			sb.append("</td>");
		}
	}

	private void generateBidPoints(StringBuffer sb, Bid bid) {
		PriorityStringLookupHelper priorityStringLookupHelper = new PriorityStringLookupHelper(
				dataSourceLookupHelper);
		sb.append("<td id=\"bidGroupReceiptTableBodyCell\">");
		for (BidProperty bidProp : bid.getBidProperties()) {
			if (bidProp.getType().equalsIgnoreCase("priority")
					|| bidProp.getType()
							.equalsIgnoreCase("leg_duration_points")) {
				for (BidPropertyEntry bidPropEntry : bidProp
						.getBidPropertyEntries()) {
					sb.append(priorityStringLookupHelper
							.getPriorityString(bidPropEntry.getEntryValue()));
				}
			}
		}
		sb.append("</td>");
	}

	private void generateCreatedDate(StringBuffer sb, Bid bid) {
		sb.append("<td id=\"bidGroupReceiptTableBodyCell\">");
		sb.append(formatDateTime(
				CWDateTime.formatISODateTime(bid.getCreated()),
				SasConstants.dateTimeFormat));
		sb.append("</td>");
	}

	private void generateUpdatedDate(StringBuffer sb, Bid bid) {
		sb.append("<td id=\"bidGroupReceiptTableBodyCell\">");
		if (bid.getUpdated() != null) {
			sb.append(formatDateTime(
					CWDateTime.formatISODateTime(bid.getUpdated()),
					SasConstants.dateTimeFormat));
		} else {
			sb.append("<br>");
		}
		sb.append("</td>");
	}

	/**
	 * Implementation of the Report interface.
	 * 
	 * @author peterp
	 */
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
			// this.buffer = buffer.toString().getBytes();
			try {
				this.buffer = buffer.toString().getBytes("UTF-8");
			} catch (UnsupportedEncodingException e) {
				LOG.error("Faild to decode");
				this.buffer = buffer.toString().getBytes();
			}
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
				mimeType = URLConnection.getFileNameMap().getContentTypeFor(
						getName());
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
	} // class GeneratedReport

	@Override
	public void setUserCustomizationAPI(UserCustomizationAPI arg0) {
		this.userCustomization = arg0;
	}

	public class customComparator implements Comparator<Bid> {
		public int compare(Bid object1, Bid object2) {
			return object1.getUpdated().isAfter(object2.getUpdated()) ? 1 : 0;
		}
	}

	@Override
	public void setDataSourceLookupHelper(
			DataSourceLookupHelper dataSourceLookupHelper) {
		this.dataSourceLookupHelper = dataSourceLookupHelper;
	}

}
