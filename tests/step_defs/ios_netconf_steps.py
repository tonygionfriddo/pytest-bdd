from pytest_bdd import scenario, given, when, then
from libs.nso import NsoLibs
import pytest


@pytest.fixture()
def nso_context():
    return NsoLibs(hostname='192.168.20.60', un='root', pw='dvrlab')


@scenario(feature_name='../features/ios_netconf.feature', scenario_name='configure an ios interface')
def test_ios_interface():
    pass


@given("setup nso")
def setup_nso(nso_context):
    # check device list for netconf device
    device_list, error = nso_context.get_device_list()
    assert error is None
    assert 'csr1000v' in device_list

    # check package list for netconf ned
    pkg_list, error = nso_context.get_packages()
    assert error is None
    assert 'cisco-iosxe-nc-1.0' in pkg_list

    # remove device trace
    result, error = nso_context.remove_device_trace(device_name='csr1000v', xml_file='remove_trace.xml')
    assert error is None
    assert result is True

    # sync device
    result, error = nso_context.sync_from_device(device_name='csr1000v')
    assert error is None
    assert result is True


@when("configuration pushed to netconf ned")
def push_config_to_ned(nso_context):
    result, error = nso_context.post_device_config(device_name='csr1000v', xml_file='interface_config.xml', config_path='ios:native/interface/')
    assert error is None
    assert result is True


@then("intended configuration saved in nso cdb")
def check_cdb_config(nso_context):
    config_dict, error = nso_context.get_device_config_dict(device_name='csr1000v', path='/config/ios:native/interface/GigabitEthernet/2/ip/address/primary')
    assert error is None
    assert config_dict['Cisco-IOS-XE-native:primary']['address'] == '1.1.1.1'
    assert config_dict['Cisco-IOS-XE-native:primary']['mask'] == '255.255.255.0'
