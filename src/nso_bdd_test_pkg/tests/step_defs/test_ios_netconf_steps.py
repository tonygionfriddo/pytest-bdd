from pytest_bdd import scenario, given, when, then, parsers
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
    nso_ssh.setup_results_path()
    nso_ssh.connect()
    return nso_ssh


@scenario(feature_name='../features/ios_netconf.feature', scenario_name='configure an ios interface')
def test_ios_interface():
    pass


@given("setup nso <ned> <device> <install_template> <interface_id> <address> <mask>")
def setup_nso(nso_context, nso_ssh, config, ned, device, install_template, interface_id, address, mask):
    config['device'] = device
    config['install_template'] = install_template
    config['trace_file'] = f"netconf-{device}.trace"
    config['ned'] = ned
    config['id'] = int(interface_id)
    config['address'] = address
    config['mask'] = mask

    # check device list for netconf device
    device_list, error = nso_context.get_device_list()
    assert not error
    assert device in device_list

    # check package list for netconf ned
    pkg_list, error = nso_context.get_packages()
    assert not error
    assert ned in pkg_list


@when("configuration pushed to netconf ned")
def push_config_to_ned(nso_context, config):
    return_code, error = nso_context.post_device_config(
        device_name=config['device'],
        template=config['install_template'],
        config=config
    )
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


@then(parsers.parse("get sync from trace {stage}"))
@given(parsers.parse("get sync from trace {stage}"))
def get_sync_from_trace(nso_context, nso_ssh, config, stage):
    # remove device trace
    return_code, error = nso_context.remove_device_trace(device_name=config['device'], xml_file='remove_trace.xml')
    assert not error
    assert return_code == 0

    # remove trace from logs dir
    return_code, status = nso_ssh.delete_file(
        path='/var/log/ncs',
        file_name=f"netconf-{config['device']}.trace"
    )
    assert status['result'] == 'success'
    assert return_code == 0

    # restart clean trace
    return_code, error = nso_context.install_device_trace(device_name=config['device'], xml_file='set_trace.xml')
    assert not error
    assert return_code == 0

    # sync device
    return_code, error = nso_context.sync_from_device(device_name=config['device'])
    assert not error
    assert return_code == 0

    # verify trace log exists
    return_code, result = nso_ssh.get_file_list(path='/var/log/ncs')
    assert return_code == 0
    assert config['trace_file'] in result['result']

    # retrieve trace file from nso
    print(nso_ssh.result_path)
    return_code, error = nso_ssh.transfer_files(
        remote_path='/var/log/ncs',
        file=f"{config['trace_file']}",
        desc=stage
    )
    assert not error
    assert return_code == 0


@given("setup test trace")
def setup_test_trace(nso_context, nso_ssh, config):
    # remove device trace
    return_code, error = nso_context.remove_device_trace(device_name=config['device'], xml_file='remove_trace.xml')
    assert not error
    assert return_code == 0

    # remove trace from logs dir
    return_code, status = nso_ssh.delete_file(
        path='/var/log/ncs',
        file_name=config['trace_file']
    )
    assert status['result'] == 'success'
    assert return_code == 0

    # restart clean trace
    return_code, error = nso_context.install_device_trace(device_name=config['device'], xml_file='set_trace.xml')
    assert not error
    assert return_code == 0


@then("get test trace")
def get_test_trace(nso_context, nso_ssh, config):
    # verify trace log exists
    return_code, result = nso_ssh.get_file_list(path='/var/log/ncs')
    assert return_code == 0
    assert config['trace_file'] in result['result']

    # retrieve trace file from nso
    return_code, error = nso_ssh.transfer_files(
        remote_path='/var/log/ncs',
        file=config['trace_file'],
        desc='test'
    )
    assert not error
    assert return_code == 0


@then("get all logs")
def get_all_logs(nso_context, nso_ssh, config):
    # get list of log files
    return_code, result = nso_ssh.get_file_list(path='/var/log/ncs')
    assert return_code == 0

    for log_file in result['result']:
        if log_file.endswith('.log'):
            # download log file to test results
            return_code, error = nso_ssh.transfer_files(
                remote_path='/var/log/ncs',
                file=log_file,
            )
            assert not error
            assert return_code == 0