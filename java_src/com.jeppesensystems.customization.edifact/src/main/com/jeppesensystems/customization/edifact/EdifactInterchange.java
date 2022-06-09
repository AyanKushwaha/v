package com.jeppesensystems.customization.edifact;

import java.util.Date;
import java.util.LinkedList;
import java.util.List;

public class EdifactInterchange extends EdifactObject {

	private String controllingAgency;
	private String level;
	private int syntaxVersionNumber;
	private String senderId;
	private String partnerId;
	private String reverseAddress;
	private String recipentId;
	private String rPartnerId;
	private String address;
	private Date preparationTime;
	private String controlReference;
	private String passwordQualifier;
	private String password;
	private List<EdifactMessage> messages;

	public EdifactInterchange(String controllingAgency, String level,
			int syntaxVersionNumber) {
		this.controllingAgency = controllingAgency;
		this.level = level;
		this.syntaxVersionNumber = syntaxVersionNumber;
	}
	
	public void setSender(String senderId, String partnerId, String reverseAddress)
	{
		this.senderId = senderId;
		this.partnerId = partnerId;
		this.reverseAddress = reverseAddress;
	}
	
	public void setRecipient(String recipientId, String rPartnerId, String address)
	{
		this.recipentId = recipientId;
		this.rPartnerId = rPartnerId;
		this.address = address;
	}

	public void setPreparationTime(Date preparationTime) {
		this.preparationTime = preparationTime;
	}
	
	public Date getPreparationTime() {
		return this.preparationTime;
	}

	public void setControlReference(String ref) {
		this.controlReference = ref;
	}
	
	public String getControlReference() {
		return this.controlReference;
	}

	public void setRecipientsReference(String password, String passwordQualifier) {
		this.password = password;
		this.passwordQualifier = passwordQualifier;
	}

	public void addMessage(EdifactMessage msg) {
		if(messages == null) messages = new LinkedList<EdifactMessage>();
		messages.add(msg);
	}

}
