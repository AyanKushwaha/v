package com.jeppesensystems.customization.edifact;

import java.io.IOException;
import java.util.Date;

public interface IEdifactReader {
	boolean dataElement(boolean mandatory) throws EdifactException, IOException;
	boolean componentDataElement(boolean mandatory) throws EdifactException, IOException;
	Date dateTime() throws EdifactException, IOException;
	int integer(int length) throws EdifactException, IOException;
	int integerMax(int maxLength) throws EdifactException, IOException;
	String alphanum(int length) throws EdifactException, IOException;
	String alphanumMax(int length) throws EdifactException, IOException;
	String alpha(int length) throws EdifactException, IOException;
	String alphaMax(int length) throws EdifactException, IOException;
	String string(int length) throws EdifactException, IOException;
	String stringMax(int length) throws EdifactException, IOException;
}
