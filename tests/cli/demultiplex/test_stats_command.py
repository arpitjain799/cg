from pathlib import Path

from click.testing import CliRunner

from cg.apps.cgstats.crud import find
from cg.apps.cgstats.stats import StatsAPI
from cg.cli.demultiplex.add import select_project_cmd
from cg.models.cg_config import CGConfig
from cg.models.demultiplex.demux_results import DemuxResults
from cg.models.demultiplex.flow_cell import FlowCell


def test_select_command(
    cli_runner: CliRunner,
    populated_stats_api: StatsAPI,
    demultiplexed_runs: Path,
    flow_cell: FlowCell,
    demultiplex_context: CGConfig,
):
    demultiplex_context.cg_stats_api_ = populated_stats_api
    # GIVEN a stats api with some information about a flowcell
    flowcell_id: str = flow_cell.id
    full_flow_cell_name: str = flow_cell.full_name
    assert populated_stats_api.find_handler.get_flow_cell_id(flowcell_id)
    demux_results = DemuxResults(
        demux_dir=demultiplexed_runs / full_flow_cell_name,
        flow_cell=flow_cell,
        bcl_converter="bcl2fastq",
    )

    # GIVEN a project id
    project_id: str = ""
    for project in demux_results.projects:
        project_id = project.split("_")[-1]
    assert project_id

    # WHEN exporting the sample information
    result = cli_runner.invoke(
        select_project_cmd, [flowcell_id, "--project", project_id], obj=demultiplex_context
    )

    # THEN assert that the command exits with success
    assert result.exit_code == 0
    # THEN assert that the flowcell id if in the printing
    assert flowcell_id in result.output
