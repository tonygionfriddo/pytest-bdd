from pytest_bdd import scenario, given, when, then
from nso_bdd_test_pkg.libs.nso import NsoLibs
from nso_bdd_test_pkg.libs.nso_ssh import NsoSshConnection
import pytest
import os


@pytest.fixture()
def nso_context():
    return NsoLibs(
        hostname=os.getenv('NSO_IP'),
        un=os.getenv('NSO_UN'),
        pw=os.getenv('NSO_PW')
    )


@pytest.fixture()
def config():
    return {}


@pytest.fixture()
def nso_ssh():
    nso_ssh = NsoSshConnection()
    nso_ssh.setup_connection(
        ip=os.getenv('NSO_IP'),
        port=os.getenv('NSO_PORT')
    )
    nso_ssh.setup_credentials(
        un=os.getenv('NSO_UN'),
        pw=os.getenv('NSO_PW')
    )
    nso_ssh.connect()
    return nso_ssh


@scenario(feature_name='../features/ios_netconf.feature', scenario_name='configure an ios interface')
def test_ios_interface():
    pass


@given("setup nso <ned> <device>")
def setup_nso(nso_context, nso_ssh, config, ned, device):
    config['device'] = device
    config['ned'] = ned
    # check device list for netconf device
    device_list, error = nso_context.get_device_list()
    assert not error
    assert device in device_list

    # check package list for netconf ned
    pkg_list, error = nso_context.get_packages()
    assert not error
    assert ned in pkg_list

    # remove device trace
    return_code, error = nso_context.remove_device_trace(device_name=device, xml_file='remove_trace.xml')
    assert not error
    assert return_code == 0

    # remove trace from logs dir
    return_code, status = nso_ssh.delete_file(
        path='/var/log/ncs',
        file_name='netconf-csr1000v.trace'
    )
    assert status['result'] == 'success'
    assert return_code == 0

    # restart clean trace
    return_code, error = nso_context.install_device_trace(device_name=device, xml_file='set_trace.xml')
    assert not error
    assert return_code == 0

    # sync device
    return_code, error = nso_context.sync_from_device(device_name=device)
    assert not error
    assert return_code == 0


@when("configuration pushed to netconf ned <device> <install_template> <id> <address> <mask>")
def push_config_to_ned(nso_context, config, device, install_template, id, address, mask):
    config['id'] = int(id)
    config['address'] = address
    config['mask'] = mask
    return_code, error = nso_context.post_device_config(device_name=device, template=install_template, config=config)
    assert not error
    assert return_code == 0


@then("intended configuration saved in nso cdb")
def check_cdb_config(nso_context, config):
    config_dict, error = nso_context.get_device_config_dict(
        device_name=config['device'],
        path=f"/config/ios:native/interface/GigabitEthernet/{config['id']}/ip/address/primary"
    )
    assert not error
    assert config_dict['Cisco-IOS-XE-native:primary']['address'] == config['address']
    assert config_dict['Cisco-IOS-XE-native:primary']['mask'] == config['mask']

    return_code, message = nso_context.check_sync(device=config['device'])
    assert return_code == 0

    return_code, message = nso_context.compare_config(device=config['device'])
    assert return_code == 0
