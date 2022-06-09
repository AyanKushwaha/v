package com.jeppesensystems.customization.edifact;

import java.io.IOException;

public interface IEdifactMessageContentProvider {
	EdifactMessageContent parse(String code, IEdifactReader reader) throws EdifactException, IOException;
}
