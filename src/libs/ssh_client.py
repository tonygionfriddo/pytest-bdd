import paramiko
import os
import datetime
import sys


class NsoSshConnection:
    # setup path for test results
    todays_datetime = datetime.date.today()
    test_time = datetime.datetime.now()
    result_path = f'../test_results/{todays_datetime.month}-{todays_datetime.day}-{todays_datetime.year}_{test_time.hour}:{test_time.minute}:{test_time.second}'

    try:
        os.mkdir('../test_results')
    except FileExistsError as e:
        if e.errno != 17:
            print(e)
            sys.exit(1)

    os.mkdir(f'../test_results/{result_path}')
    print(result_path)

    # setup ssh connection
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='192.168.20.60', username='root', password='dvrlab')

    # get file list
    _stdin, stdout, _stderr = ssh_client.exec_command('cd /var/log/ncs && ls')
    output = [x.rstrip() for x in stdout.readlines()]
    print(output)

    # create a file
    _stdin, stdout, _stderr = ssh_client.exec_command('touch /var/log/ncs/test.msg')
    _stdin, stdout, _stderr = ssh_client.exec_command('cd /var/log/ncs && ls')
    output = [x.rstrip() for x in stdout.readlines()]
    print(output)

    # delete a file
    _stdin, stdout, _stderr = ssh_client.exec_command('rm -rf /var/log/ncs/test.msg')
    _stdin, stdout, _stderr = ssh_client.exec_command('cd /var/log/ncs && ls')
    output = [x.rstrip() for x in stdout.readlines()]
    print(output)

    # transfer files
    ftp_client = ssh_client.open_sftp()
    ftp_client.get('/var/log/ncs/ncs-python-vm.log', f'{result_path}/ncs-python-vm.log')

    # cleanup connections
    ftp_client.close()
    ssh_client.close()


if __name__ == '__main__':
    nso = NsoSshConnection()
