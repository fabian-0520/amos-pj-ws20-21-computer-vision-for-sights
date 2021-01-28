def test_get_start_command() -> None:
    from cron_jobs.mts_ec2_communication import _get_start_command

    docker_run_command = _get_start_command('kyoto')
    assert docker_run_command == 'sudo sh mts/mts.sh host 1337 database user password kyoto 100'
