def test_get_docker_run_command_gpu_enabled() -> None:
    from cron_jobs.mts_ec2_communication import _get_docker_run_command

    docker_run_command = _get_docker_run_command('tokyo')
    assert docker_run_command == 'sudo docker run -d --ipc=host --gpus all ' \
                                 '-e PGHOST=test -e PGDATABASE=test -e PGUSER=test ' \
                                 '-e PGPORT=test -e PGPASSWORD=test -e city=tokyo -it mts'


def test_get_docker_run_command_gpu_disabled(monkeypatch) -> None:
    from cron_jobs.mts_ec2_communication import _get_docker_run_command
    monkeypatch.setenv("IS_MTS_GPU_ENABLED", "False")

    docker_run_command = _get_docker_run_command('kyoto')
    assert docker_run_command == 'sudo docker run -d ' \
                                 '-e PGHOST=test -e PGDATABASE=test -e PGUSER=test ' \
                                 '-e PGPORT=test -e PGPASSWORD=test -e city=kyoto -it mts'
