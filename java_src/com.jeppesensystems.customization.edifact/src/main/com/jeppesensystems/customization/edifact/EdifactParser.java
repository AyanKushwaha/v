package com.jeppesensystems.customization.edifact;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.TimeZone;

public class EdifactParser {
	private byte componentDataElemSep, dataElemSep, dot, escape, space, term;
	private boolean strictTelex = false;
	private boolean useLevelBCharacterSet = false; // Not currently supported
	private TimeZone timeZone = TimeZone.getTimeZone("UTC");
	private Map<String, IEdifactMessageContentProvider> messageContent = new HashMap<String, IEdifactMessageContentProvider>();
	public EdifactParser() {

	}

	public void parse(InputStream strm) throws EdifactException, IOException {
		if(!strm.markSupported()) {
			strm = new BufferedInputStream(strm);
		}
		int u = strm.read();
		int n = strm.read();
		int a = strm.read();
		byte[] sep = new byte[6];
		if (u != 85 || n != 78 || a != 65) {
			// No 'UNA' segment. Use default separators
			sep[0] = 58; sep[1] = 43; sep[2] = 46;
			sep[3] = 63; sep[4] = 32; sep[5] = 39;
		} else {
			strm.read(sep);
			for (int i = 0; i < 5; i++) {
				for (int j = i + 1; j < 6; j++) {
					if (sep[i] == sep[j]) {
						throw new EdifactNotWellformedException(
								"Separator char conflict");
					}
				}
			}
		}
		componentDataElemSep = sep[0];
		dataElemSep = sep[1];
		dot = sep[2];
		escape = sep[3];
		space = sep[4];
		term = sep[5];
		parseInterchange(strm);
	}
	
	public void addMessageContent(String code, IEdifactMessageContentProvider provider)
	{
		messageContent.put(code, provider);
	}
	
	private EdifactInterchange parseInterchange(InputStream strm) throws EdifactException, IOException
	{
		String code = alpha(3, strm);
		if (!code.equals("UNB")) {
			throw new EdifactNotWellformedException("Expected interchange header, but got " + code);
		}
		// Syntax identifier
		dataElement(true, strm);
		String controllingAgency = alpha(3, strm);
		String level = alpha(1, strm);
		componentDataElement(true, strm);
		int syntaxVersionNumber = integer(1, strm);
		// Interchange sender
		dataElement(true, strm);
		String senderId = alphanumMax(35, strm);
		String partnerId = null, reverseAddress = null;
		if(componentDataElement(false, strm)) {
			partnerId = alphanumMax(4, strm);
			if(componentDataElement(false, strm)) {
				reverseAddress = alphanumMax(14, strm);
			}
		}
		// Interchange recipient
		dataElement(true, strm);
		String recipientId = alphanumMax(35, strm);
		String rPartnerId = null, address = null;
		if(componentDataElement(false, strm)) {
			rPartnerId = alphanumMax(4, strm);
			if(componentDataElement(false, strm)) {
				address = alphanumMax(14, strm);
			}
		}
		// Date/time of preparation
		dataElement(true, strm);
		Date dateTime = dateTime(strm);
		dataElement(true, strm);
		// Interchange control reference
		String ref = alphanumMax(14, strm);
		
		EdifactInterchange ic = new EdifactInterchange(controllingAgency, level, syntaxVersionNumber);
		ic.setSender(senderId, partnerId, reverseAddress);
		ic.setRecipient(recipientId, rPartnerId, address);
		ic.setPreparationTime(dateTime);
		ic.setControlReference(ref);
		
		System.err.println("Message " + controllingAgency + " " + level + " : " + syntaxVersionNumber + " - " + senderId);
		System.err.println("  from " + senderId + " : " + partnerId + " : " + reverseAddress);
		System.err.println("    to " + recipientId + " : " + rPartnerId + " : " + address);
		System.err.println("    at " + dateTime + " ref " + ref);
		
		// Interchange recipients reference
		if(dataElement(false, strm)) {
			String password = alphanumMax(14, strm);
			String passwordQualifier = null;
			if(componentDataElement(false, strm)) {
				passwordQualifier = alphanum(2, strm);
			}
			ic.setRecipientsReference(password, passwordQualifier);
			System.err.println("Password " + password + " qual " + passwordQualifier);
			if(dataElement(false, strm)) {
				// application reference etc
				//http://www.unece.org/trade/untdid/texts/d422_d.htm#ab
				throw new EdifactNotWellformedException("Notimpl");
			}
		}
		int msgCount = 0;
		while(true) {
			code = alpha(3, strm);
			if(code.equals("UNG")) {
				parseFunctionalGroup(strm);
			} else if (code.equals("UNH")) {
				EdifactMessage msg = parseMessage(strm);
				ic.addMessage(msg);
				msgCount++;
			} else if (code.equals("UNZ")) {
				dataElement(true, strm);
				int count = integerMax(6, strm);
				if(count != msgCount) {
					throw new EdifactNotWellformedException("Message count " + count + " mismatch actual " + msgCount);
				}
				dataElement(true, strm);
				String trailingRef = alphanumMax(14, strm);
				if(!trailingRef.equals(ref)) {
					throw new EdifactNotWellformedException("Refno of 'UNZ' is " + trailingRef + ", expected same as 'UNB': " + ref);
				}
				term(strm);
				break;
			} else {
				throw new EdifactNotWellformedException("Expected UNG or UNH, got " + code);
			}
		}
		return ic;
	}
	
	private void parseFunctionalGroup(InputStream strm) throws EdifactException, IOException
	{
		System.err.println("Functional group");
	}
	
	private EdifactMessage parseMessage(InputStream strm) throws EdifactException, IOException
	{
		System.err.println("Message");
		dataElement(true, strm);
		String refno = alphanumMax(14, strm);
		dataElement(true, strm);
		String type = alphanumMax(6, strm);
		componentDataElement(true, strm);
		String version = alphanumMax(3, strm);
		componentDataElement(true, strm);
		String revision = alphanumMax(3, strm);
		componentDataElement(true, strm);
		String controllingAgency = alphanumMax(2, strm);
		System.err.println("* Message " + refno + " type " + type + " : " + version + " : " + controllingAgency);
		EdifactMessage msg = new EdifactMessage(refno, type, version, revision, controllingAgency);
		if(componentDataElement(false, strm)) {
			String associationCode = alphanumMax(6, strm);
			System.out.println("*  Assoc " + associationCode);
			msg.setAssociationCode(associationCode);
		}
		if(dataElement(false, strm)) {
			String commonAccessReference = alphanumMax(35, strm);
			System.out.println("*  Common Ref " + commonAccessReference);
			msg.setCommonAccessReference(commonAccessReference);
			if(dataElement(false, strm)) {
				int sequenceNumber = integerMax(2, strm);
				msg.setSequenceNumber(sequenceNumber);
				if(componentDataElement(false, strm)) {
					switch(alpha(1, strm).charAt(0)) {
					case 'C':
						msg.setIsFirst(true);
						break;
					case 'F':
						msg.setIsLast(true);
						break;
					}
				}
			}
		}
		int msgcnt = 2;
		while(true) {
			String code = alpha(3, strm);
			if(code.equals("UNT")) {
				dataElement(true, strm);
				int count = integerMax(6, strm);
				if(count != msgcnt) {
					throw new EdifactNotWellformedException("Segment count " + count + " mismatch actual " + msgcnt);
				}
				dataElement(true, strm);
				String trailingRef = alphanumMax(14, strm);
				if(!trailingRef.equals(refno)) {
					throw new EdifactNotWellformedException("Refno of 'UNT' is " + trailingRef + ", expected same as 'UNH': " + refno);
				}
				term(strm);
				break;
			} else if(code.equals("UNZ") || code.equals("UNE") || code.equals("UNA") || code.equals("UNB") || code.equals("UNG") || code.equals("UNH")) {
				throw new EdifactNotWellformedException("Unexpected segment type '" + code + "' before 'UNT'");
			} else {
				EdifactMessageContent content = parseMessageContent(code, strm);
				swallowIf(term, strm);
				msgcnt++;
			}
		}
		return msg;
	}
	
	EdifactMessageContent parseMessageContent(String code, InputStream strm) throws EdifactException, IOException
	{
		IEdifactMessageContentProvider provider = messageContent.get(code);
		if(provider == null) {
			System.err.println("Do not know how to parse content for "+code);
			skipToTerminator(strm);
		}
		return null;
	}

	private boolean dataElement(boolean mandatory, InputStream strm) throws EdifactException, IOException
	{
		int ch = next(strm);
		if(ch == dataElemSep) return true;
		else if(ch == componentDataElemSep) throw new EdifactNotWellformedException("Expected data element separator but got component separator");
		if(mandatory) {
			throw new EdifactNotWellformedException("Expected data element separator but got " + stringFromInts(ch));
		} else {
			if (ch == term) return false;
			throw new EdifactNotWellformedException("Expected data element separator or terminator, but got " + stringFromInts(ch));
		}
	}
	
	private boolean componentDataElement(boolean mandatory, InputStream strm) throws EdifactException, IOException
	{
		strm.mark(100);
		int ch = next(strm);
		if(ch == componentDataElemSep) return true;
		if(mandatory) {
			throw new EdifactNotWellformedException("Expected data element separator but got " + stringFromInts(ch));
		} else {
			if (ch == dataElemSep || ch == term) {
				strm.reset();
				return false;
			}
			throw new EdifactNotWellformedException("Expected data element separator or terminator, but got " + stringFromInts(ch));
		}
	}

	private void term(InputStream strm) throws EdifactException, IOException
	{
		int s = next(strm);
		if(s != term) throw new EdifactNotWellformedException("Expected terminator, got " + stringFromInts(s));
	}

	private void swallowIf(int charToSwallow, InputStream strm) throws EdifactException, IOException
	{
		strm.mark(1);
		if(next(strm) != charToSwallow) strm.reset();
	}
	
	private void skipToTerminator(InputStream strm) throws EdifactException, IOException {
		while(next(strm) != term);
	}

	private Date dateTime(InputStream strm) throws EdifactException, IOException
	{
		int year = integer(2, strm);
		if(year >= 70) year = 1900+year;
		else year = 2000+year;
		int month = integer(2, strm);
		int day = integer(2, strm);
		componentDataElement(true, strm);
		int hour = integer(2, strm);
		int minute = integer(2, strm);
		Calendar cal = Calendar.getInstance(getTimeZone());
		cal.set(year, month-1, day, hour, minute);
		return cal.getTime();
	}

	private int integer(int length, InputStream strm) throws EdifactException, IOException
	{
		return Integer.parseInt(string(length, strm, false, true, false));
	}

	private int integerMax(int maxLength, InputStream strm) throws EdifactException, IOException
	{
		return Integer.parseInt(stringMax(maxLength, strm, false, true, false));
	}
	
	private String alphanum(int length, InputStream strm) throws EdifactException, IOException
	{
		return string(length, strm, true, true, false);
	}
	
	private String alpha(int length, InputStream strm) throws EdifactException, IOException
	{
		return string(length, strm, true, false, false);
	}
	
	private String alphanumMax(int length, InputStream strm) throws EdifactException, IOException
	{
		return stringMax(length, strm, true, true, false);
	}

	private String string(int length, InputStream strm, boolean allowAlpha, boolean allowNumeric, boolean allowOther) throws EdifactException, IOException
	{
		byte[] buf = new byte[length];
		for(int i=0;i<length;i++) {
			int bt = next(strm);
			if(bt == dataElemSep || bt == componentDataElemSep || bt == term) {
				throw new EdifactNotWellformedException("String is too short, unexpected item termination");
			}
			buf[i] = (byte)bt;
		}
		return new String(buf, "latin1");
	}

	private String stringMax(int maxLength, InputStream strm, boolean allowAlpha, boolean allowNumeric, boolean allowOther) throws EdifactException, IOException
	{
		byte[] buf = new byte[maxLength];
		int length = -1;
		for(int i=0;i<maxLength+1;i++) {
			strm.mark(1);
			int bt = next(strm);
			if(bt == dataElemSep || bt == componentDataElemSep || bt == term) {
				strm.reset();
				length = i;
				break;
			} else if(i>=maxLength) break;
			buf[i] = (byte)bt;
		}
		if(length > 0) maxLength = length;
		String str = new String(buf, 0, maxLength, "latin1");
		if(length == -1) {
			throw new EdifactNotWellformedException("String '"+str+"...' is too long, expected max " + maxLength + " characters");
		}
		return str;
	}
	
	private int next(InputStream strm) throws EdifactException, IOException
	{
		while(true) {
			int ch = strm.read();
			if(ch >= 65 && ch <= 90) { // A-Z
				return ch;
			} else if(ch >= 97 && ch <= 122) { // a-z
				return ch;
			} else if(ch >= 48 && ch <= 57) { // a-z
				return ch;
			} else if(ch == componentDataElemSep || ch == dataElemSep || ch == dot || ch == escape || ch == space || ch == term) { // a-z
				return ch;
			} else {
				switch(ch) {
				case 10: // <lf>
				case 13: // <cr>
					break;
				case 32: // ' '
				case 46: // '.'
				case 44: // ','
				case 45: // '-'
				case 40: // '('
				case 41: // ')'
				case 47: // '/'
				case 61: // '='
					return ch;
				case 33: // '!'
				case 34: // '"'
				case 37: // '%'
				case 38: // '&'
				case 42: // '*'
				case 59: // ';'
				case 60: // '<'
				case 62: // '>'
					if(strictTelex) {
						throw new EdifactNotWellformedException("Character '" + stringFromInts(ch) + "' not valid in current character set (Intl/Telex)");
					}
					return ch;
				default:
					// TODO: Check if another charset is explicity set
					throw new EdifactNotWellformedException("Character '" + stringFromInts(ch) + "' not valid in current character set (7-bit ascii)");
				}
			}
		}
	}
	
	private static String stringFromInts(Integer... ints)
	{
		byte[] buf = new byte[ints.length];
		for(int i=0;i<ints.length;i++) {
			buf[i] = ints[i].byteValue();
		}
		try {
			return new String(buf, "latin1");
		} catch (UnsupportedEncodingException e) {
			return "<bad encoding>";
		}
	}

	public void setTimeZone(TimeZone timeZone) {
		this.timeZone = timeZone;
	}

	public TimeZone getTimeZone() {
		return timeZone;
	}
}
