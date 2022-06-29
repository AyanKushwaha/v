package com.jeppesen.carmen.customization.sas.e2e.fixtures.api;

import java.util.UUID;
import java.util.function.UnaryOperator;

import static java.util.Objects.isNull;

/**
 * Could be used as test-data generator source in before method for e2e or integration tests.
 *
 * @param <T> type of entity.
 */
public interface Fixture<T> {

    /**
     * In simple case, it's just reusing spring-data repository to create object
     * passed as an argument.
     *
     * @param obj new entity
     * @return persisted entity.
     */
    T create(final T obj);

    /**
     * @return draft basis of object to be saved during create method.
     */
    T initDraft();

    /**
     * Could be refactored in using apache commons get alphabetic strings if UUID is not enough.
     *
     * @return generated UUID string representation.
     */
    default String uuid() {
        return UUID.randomUUID().toString();
    }

    /**
     * Generated string by size
     *
     * @return first size chars of generated UUID string representation.
     */
    default String generateString(final int size) {
        return generateString("", size);
    }

    /**
     * Generated string by it's prefix and size
     *
     * @return first size chars of generated UUID string representation.
     */
    default String generateString(final String prefix, final int size) {

        if (size < 1) return "";

        final String uuid = uuid();
        final int maxLen = uuid.length();
        final int len = size > maxLen ? maxLen : size;
        final String total = isNull(prefix) || prefix.trim().isEmpty() ? uuid : prefix.concat(uuid);

        return total.substring(0, len);
    }

    default T create(final UnaryOperator<T> patched) {
        return create(patched.apply(initDraft()));
    }
}
