package com.sas.interbids.base;

/**
 * Defines the number of bids of type 'flight' allowed per particular priority.
 */

public enum BidsPerPriority {

    LOW("1", 2),
    MEDIUM("2", 2),
    HIGH("3", 1);

    private final String priorityValue;
    private final int allowedBidsAmount;

    /**
     * @param priorityValue - refers to values defined in {@link com.sas.interbids.datasources.PriorityDataSource PriorityDataSource.class}
     * @param allowedBidsAmount  - number of bids allowed per priority
     */
    BidsPerPriority(final String priorityValue, final int allowedBidsAmount) {
        this.priorityValue = priorityValue;
        this.allowedBidsAmount = allowedBidsAmount;
    }

    public String getPriorityValue() {
        return priorityValue;
    }

    public int getAllowedBidsAmount() {
        return allowedBidsAmount;
    }

    public static BidsPerPriority fromPriorityValue(String priorityValue) {
        for (BidsPerPriority b : values()) {
            if (priorityValue.equalsIgnoreCase(b.getPriorityValue())) {
                return b;
            }
        }
        throw new IllegalArgumentException("No allowed amount defined for bid with priority value" + priorityValue);
    }
}
