package com.jeppesen.carmen.customization.sas.e2e.infrastructure;

import lombok.NoArgsConstructor;

import java.util.Arrays;
import java.util.Optional;

import static java.lang.String.format;
import static java.util.stream.Collectors.joining;
import static lombok.AccessLevel.PRIVATE;

@NoArgsConstructor(access = PRIVATE)
public class Strings {

    public static String trimLine(String string) {
        String[] parts = string.split("\\s*\\r?\\n\\s*");
        return Arrays.stream(parts)
                .map(String::trim)
                .collect(joining(", "));
    }

    public static String trimmed(String payload, String fieldName) {
        return Optional.ofNullable(payload)
                .filter(name -> !name.trim().isEmpty())
                .orElseThrow(() -> new RuntimeException(format("%s may not be null or empty", fieldName)));
    }
}
