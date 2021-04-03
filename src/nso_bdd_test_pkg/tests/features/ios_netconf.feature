Feature: cisco ios netconf ned
  validate required netconf configurations through cisco netconf ned

  Scenario Outline: configure an ios interface
    Given setup nso <ned> <device> <install_template> <interface_id> <address> <mask>
    And get sync from trace pre
    And setup test trace
    When configuration pushed to netconf ned
    Then intended configuration saved in nso cdb
    And get test trace
    And get sync from trace post
    And get all logs

    Examples:
    | ned                  | device   | install_template             | interface_id  | address     | mask            |
    | csr1000v-nc-1.0.0    | csr1000v | /create/interface_config.xml | 3   | 44.44.44.44 | 255.255.255.0   |
#    | csr1000v-nc-1.0.0    | csr1000v | /create/interface_config.xml | 2   | 22.22.22.22 | 255.255.255.0   |
#    | csr1000v-nc-1.0.0    | csr1000v | /create/interface_config.xml | 3   | 33.33.33.33 | 255.255.255.0   |
#    | csr1000v-nc-1.0.0    | csr1000v | /create/interface_config.xml | 2   | 55.55.55.55 | 255.255.255.0   |
#    | csr1000v-nc-1.0.0    | csr1000v | /create/interface_config.xml | 3   | 66.66.66.66 | 255.255.255.0   |
#    | csr1000v-nc-1.0.0    | csr1000v | /create/interface_config.xml | 2   | 77.77.77.77 | 255.255.255.0   |
#    | csr1000v-nc-1.0.0    | csr1000v | /create/interface_config.xml | 3   | 88.88.88.88 | 255.255.255.0   |
#    | csr1000v-nc-1.0.0    | csr1000v | /create/interface_config.xml | 2   | 99.99.99.99 | 255.255.255.0   |