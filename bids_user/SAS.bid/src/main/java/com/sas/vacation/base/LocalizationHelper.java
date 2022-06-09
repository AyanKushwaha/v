package com.sas.vacation.base;

import com.jeppesen.jcms.crewweb.common.localization.Localization;

import java.text.MessageFormat;

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
