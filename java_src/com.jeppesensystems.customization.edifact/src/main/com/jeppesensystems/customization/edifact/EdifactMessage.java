package com.jeppesensystems.customization.edifact;

public class EdifactMessage extends EdifactObject {

	private String refno;
	private String type;
	private String version;
	private String revision;
	private String controllingAgency;
	private String associationCode;
	private String commonAccessReference;
	private boolean isFirst;
	private boolean isLast;
	private int sequenceNumber;

	public EdifactMessage(String refno, String type, String version, String revision,
			String controllingAgency) {
		this.setRefno(refno);
		this.setType(type);
		this.setVersion(version);
		this.setControllingAgency(controllingAgency);
	}

	public void setRefno(String refno) {
		this.refno = refno;
	}

	public String getRefno() {
		return refno;
	}

	public void setType(String type) {
		this.type = type;
	}

	public String getType() {
		return type;
	}

	public void setVersion(String version) {
		this.version = version;
	}

	public String getVersion() {
		return version;
	}

	public void setRevision(String revision) {
		this.revision = revision;
	}

	public String getRevision() {
		return revision;
	}

	public void setControllingAgency(String controllingAgency) {
		this.controllingAgency = controllingAgency;
	}

	public String getControllingAgency() {
		return controllingAgency;
	}

	public void setAssociationCode(String associationCode) {
		this.associationCode = associationCode;
	}
	
	public String getAssociationCode() {
		return associationCode;
	}

	public void setCommonAccessReference(String commonAccessReference) {
		this.commonAccessReference = commonAccessReference;
	}
	
	public String getCommonAccessReference() {
		return commonAccessReference;
	}

	public void setIsFirst(boolean b) {
		this.isFirst = b;
	}

	public void setIsLast(boolean b) {
		this.isLast = b;
	}
	
	public boolean isFirst() {
		return isFirst;
	}
	
	public boolean isLast() {
		return isLast;
	}

	public void setSequenceNumber(int sequenceNumber) {
		this.sequenceNumber = sequenceNumber;
	}
	
	public int getSequenceNumber() {
		return sequenceNumber;
	}
}
