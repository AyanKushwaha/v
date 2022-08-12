@skip
Feature: Optimization Peformance

  # @opt
  # Scenario: run an opt job and verify performance

  #   Given I load the plan "Jeppesen/2012Apr/FC_737_WEEKLY/ex_optimization"
  #   When I run the pairing optimizer
  #   Then the last solution shall have the following results
  #   | element     | value   |
  #   | performance | 0:03:11 |
  #   | TOTAL cost  | 663836  |
  #   and performance shall be about 3:11
  #   and the "TOTAL cost" shall be about 663836

  Scenario: fake an opt job and verify performance (for debugging)

    Given I load the plan "Jeppesen/2012Apr/FC_737_WEEKLY/ex_optimization"
    When I fake the pairing optimizer
    Then the last solution shall have the following results
    | element     | value   |
    | performance | 0:04:09 |
    | TOTAL cost  | 663836  |
    and performance shall be about 0:04:09
    and the "TOTAL cost" shall be about 663836

