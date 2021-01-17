"""This module takes care of the MTS EC2 communication."""
import boto3
import os
import paramiko
from data.sql_exec import exec_sql
from time import sleep

ec2_client = boto3.client('ec2',
                          os.environ['AWS_REGION'],
                          aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=os.environ['AWS_ACCESS_KEY'])


def boot_mts_ec2_instance() -> None:
    """Boots the EC2 instance of the MTS."""
    ec2_client.start_instances(
        InstanceIds=[os.environ['MTS_EC2_INSTANCE_ID']],
        DryRun=False
    )
    sleep(30)


def is_mts_ec2_instance_running() -> bool:
    """Returns whether the MTS is currently active and training.

    Returns
    -------
    is_running: bool
        Whether the MTS is already training.
    """
    response = ec2_client.describe_instance_status(InstanceIds=[os.environ['MTS_EC2_INSTANCE_ID']])
    return len(response['InstanceStatuses']) > 0 and \
           response['InstanceStatuses'][0]['InstanceState']['Name'] == 'running'


def stop_mts_ec2_instance_after_training(city: str) -> None:
    """Stops the MTS EC2 instance after successful training.

    Parameters
    ----------
    city: str
        Name of the city the MTS currently trains for.
    """
    training_completed_query = f"""
        SELECT count(*) 
        FROM data_mart_layer.current_trained_models 
        WHERE upper(city_name) = '{city.upper()}'
    """
    while exec_sql(training_completed_query, return_result=True) == 0:
        sleep(60)

    ec2_client.stop_instances(
        InstanceIds=[os.environ['MTS_EC2_INSTANCE_ID']],
        Hibernate=False,
        DryRun=False,
        Force=False
    )


def trigger_mts_training(city: str) -> None:
    """Triggers the MTS for training based on the given city.

    Parameters
    ----------
    city: str
        City to train on.
    """
    response = ec2_client.describe_instances(InstanceIds=[os.environ['MTS_EC2_INSTANCE_ID']])
    public_url = response['Reservations'][0]['Instances'][0]['PublicDnsName']

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=public_url,
                       username='ubuntu',
                       pkey=paramiko.RSAKey.from_private_key_file('../ec2key.pem'))
    ssh_client.exec_command(_get_docker_run_command(city))
    ssh_client.close()


def _get_docker_run_command(city: str) -> str:
    """Returns the docker run command needed for the MTS in order to train on the given city.

    Parameters
    ----------
    city: str
        City the MTS should train on.

    Returns
    -------
    docker_run_command: str
        Corresponding docker run command.
    """
    prefix = 'sudo docker run -d'
    prefix += '' if os.environ['IS_MTS_GPU_ENABLED'].upper() == 'FALSE' else ' --ipc=host --gpus all'

    return f'{prefix} ' \
           f'-e PGHOST={os.environ["PGHOST"]} ' \
           f'-e PGDATABASE={os.environ["PGDATABASE"]} ' \
           f'-e PGUSER={os.environ["PGUSER"]} ' \
           f'-e PGPORT={os.environ["PGPORT"]} ' \
           f'-e PGPASSWORD={os.environ["PGPASSWORD"]} ' \
           f'-e city={city} ' \
           f'-it mts'
