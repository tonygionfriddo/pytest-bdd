Feature: cisco ios netconf ned
  validate required netconf configurations through cisco netconf ned

  Scenario: configure an ios interface
    Given setup nso
    When configuration pushed to netconf ned
    Then intended configuration saved in nso cdb
