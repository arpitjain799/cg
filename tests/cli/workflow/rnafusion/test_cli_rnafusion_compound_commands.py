import logging
from pathlib import Path

from cg.apps.hermes.hermes_api import HermesApi
from cg.apps.hermes.models import CGDeliverables
from cg.cli.workflow.rnafusion.base import rnafusion, start, store, start_available, store_available
from cg.models.cg_config import CGConfig
from click.testing import CliRunner
from cg.meta.workflow.rnafusion import RnafusionAnalysisAPI


EXIT_SUCCESS = 0


def test_rnafusion_no_args(cli_runner: CliRunner, rnafusion_context: CGConfig):
    """Test to see that running BALSAMIC without options prints help and doesn't result in an error"""
    # GIVEN no arguments or options besides the command call

    # WHEN running command
    result = cli_runner.invoke(rnafusion, [], obj=rnafusion_context)

    # THEN command runs successfully
    assert result.exit_code == EXIT_SUCCESS

    # THEN help should be printed
    assert "help" in result.output


def test_start(cli_runner: CliRunner, rnafusion_context: CGConfig, caplog):
    """Test to ensure all parts of start command will run successfully given ideal conditions"""
    caplog.set_level(logging.INFO)

    # GIVEN case id for which we created a config file
    case_id = "rnafusion_case_enough_reads"

    # GIVEN decompression is not needed
    RnafusionAnalysisAPI.resolve_decompression.return_value = None

    # WHEN dry running with dry specified
    result = cli_runner.invoke(start, [case_id, "--dry-run"], obj=rnafusion_context)

    # THEN command should execute successfully
    assert result.exit_code == EXIT_SUCCESS
    assert case_id in caplog.text


def test_store(
    cli_runner: CliRunner,
    rnafusion_context: CGConfig,
    real_housekeeper_api,
    mock_deliverable,
    mock_analysis_finish,
    caplog,
    hermes_deliverables,
    mocker,
):
    """Test to ensure all parts of store command are run successfully given ideal conditions"""
    caplog.set_level(logging.INFO)

    # GIVEN case-id for which we created a config file, deliverables file, and analysis_finish file
    case_id = "rnafusion_case_enough_reads"

    # Set Housekeeper to an empty real Housekeeper store
    rnafusion_context.housekeeper_api_ = real_housekeeper_api
    rnafusion_context.meta_apis["analysis_api"].housekeeper_api = real_housekeeper_api

    # Make sure the bundle was not present in hk
    assert not rnafusion_context.housekeeper_api.bundle(case_id)

    # Make sure analysis not already stored in status_db
    assert not rnafusion_context.status_db.family(case_id).analyses

    # GIVEN that HermesAPI returns a deliverables output
    mocker.patch.object(HermesApi, "convert_deliverables")
    HermesApi.convert_deliverables.return_value = CGDeliverables(**hermes_deliverables)

    # WHEN running command
    result = cli_runner.invoke(store, [case_id], obj=rnafusion_context)
    # THEN bundle should be successfully added to HK and STATUSDB
    assert result.exit_code == EXIT_SUCCESS
    assert "Analysis successfully stored in Housekeeper" in caplog.text
    assert "Analysis successfully stored in StatusDB" in caplog.text
    assert rnafusion_context.status_db.family(case_id).analyses
    assert rnafusion_context.housekeeper_api.bundle(case_id)


#
def test_start_available(cli_runner: CliRunner, rnafusion_context: CGConfig, caplog, mocker):
    """Test to ensure all parts of compound start-available command are executed given ideal conditions
    Test that start-available picks up eligible cases and does not pick up ineligible ones"""
    caplog.set_level(logging.INFO)

    # GIVEN CASE ID of sample where read counts pass threshold
    case_id_success = "rnafusion_case_enough_reads"

    # Ensure the config is mocked to run compound command
    Path.mkdir(
        Path(
            rnafusion_context.meta_apis["analysis_api"].get_case_config_path(case_id_success)
        ).parent,
        exist_ok=True,
    )
    Path(rnafusion_context.meta_apis["analysis_api"].get_case_config_path(case_id_success)).touch(
        exist_ok=True
    )

    # GIVEN decompression is not needed
    mocker.patch.object(RnafusionAnalysisAPI, "resolve_decompression")
    RnafusionAnalysisAPI.resolve_decompression.return_value = None

    # WHEN running command
    result = cli_runner.invoke(start_available, ["--dry-run"], obj=rnafusion_context)

    # THEN command exits with 0
    assert result.exit_code == 0

    # THEN it should successfully identify the one case eligible for auto-start
    assert case_id_success in caplog.text


def test_store_available(
    tmpdir_factory,
    cli_runner: CliRunner,
    rnafusion_context: CGConfig,
    real_housekeeper_api,
    mock_config,
    mock_deliverable,
    caplog,
    mocker,
    hermes_deliverables,
):
    """Test to ensure all parts of compound store-available command are executed given ideal conditions
    Test that sore-available picks up eligible cases and does not pick up ineligible ones"""
    caplog.set_level(logging.INFO)

    # GIVEN CASE ID of sample where read counts pass threshold
    case_id_success = "rnafusion_case_enough_reads"

    # GIVEN CASE ID where analysis finish is not mocked
    case_id_fail = "rnafusion_case_not_finished"

    # Ensure the config is mocked for fail case to run compound command
    Path.mkdir(
        Path(rnafusion_context.meta_apis["analysis_api"].get_case_config_path(case_id_fail)).parent,
        exist_ok=True,
    )
    Path(rnafusion_context.meta_apis["analysis_api"].get_case_config_path(case_id_fail)).touch(
        exist_ok=True
    )

    # GIVEN that HermesAPI returns a deliverables output
    mocker.patch.object(HermesApi, "convert_deliverables")
    HermesApi.convert_deliverables.return_value = CGDeliverables(**hermes_deliverables)
    #
    # Ensure case was successfully picked up by start-available and status set to running
    result = cli_runner.invoke(start_available, ["--dry-run"], obj=rnafusion_context)
    rnafusion_context.status_db.family(case_id_success).action = "running"
    rnafusion_context.status_db.commit()

    # THEN command exits with 1 because one of the cases threw errors
    assert result.exit_code == 1
    assert case_id_success in caplog.text
    assert rnafusion_context.status_db.family(case_id_success).action == "running"

    rnafusion_context.housekeeper_api_ = real_housekeeper_api
    rnafusion_context.meta_apis["analysis_api"].housekeeper_api = real_housekeeper_api

    # WHEN running command
    result = cli_runner.invoke(store_available, obj=rnafusion_context)

    # THEN command exits successfully
    assert result.exit_code == 0

    # THEN case id with analysis_finish gets picked up
    assert case_id_success in caplog.text

    # THEN case has analyses
    assert rnafusion_context.status_db.family(case_id_success).analyses

    # THEN bundle can be found in Housekeeper
    assert rnafusion_context.housekeeper_api.bundle(case_id_success)

    # THEN bundle added successfully and action set to None
    assert rnafusion_context.status_db.family(case_id_success).action is None
