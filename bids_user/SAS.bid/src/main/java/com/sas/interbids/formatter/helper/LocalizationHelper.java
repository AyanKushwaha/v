package com.sas.interbids.formatter.helper;

import java.text.MessageFormat;

import com.jeppesen.jcms.crewweb.common.localization.Localization;

public class LocalizationHelper {

	private Localization localization;

	public LocalizationHelper(Localization localization) {
		this.localization = localization;
	}

	public String format(String key, Object... arguments) {
		String s = localization.MSGR(key);
		return MessageFormat.format(s, arguments);
	}
}
