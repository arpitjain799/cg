"""CLI support to start microsalt"""

import datetime as dt
import logging
from pathlib import Path
from typing import Any, List, Optional

import click
from cg.cli.workflow.commands import resolve_compression, store, store_available
from cg.constants import EXIT_FAIL, EXIT_SUCCESS, Pipeline
from cg.constants.constants import FileFormat
from cg.exc import CgError
from cg.io.controller import WriteStream, WriteFile
from cg.meta.workflow.microsalt import MicrosaltAnalysisAPI
from cg.models.cg_config import CGConfig
from cg.store.models import Analysis, Sample
from housekeeper.store.models import File
from cg.meta.workflow.analysis import AnalysisAPI

LOG = logging.getLogger(__name__)

OPTION_DRY_RUN = click.option(
    "-d",
    "--dry-run",
    help="Print command to console without executing",
    is_flag=True,
)
OPTION_SAMPLE = click.option(
    "-s",
    "--sample",
    help="Start workflow by providing a sample_id (By default case_id will be used)",
    is_flag=True,
)
OPTION_TICKET = click.option(
    "-t",
    "--ticket",
    help="Start workflow by providing a ticket_id (By default case_id will be used)",
    is_flag=True,
)
ARGUMENT_UNIQUE_IDENTIFIER = click.argument("unique_id", required=True, type=click.STRING)


@click.group(invoke_without_command=True)
@click.pass_context
def microsalt(context: click.Context) -> None:
    """Microbial workflow"""
    AnalysisAPI.get_help(context)
    context.obj.meta_apis["analysis_api"] = MicrosaltAnalysisAPI(
        config=context.obj,
    )


microsalt.add_command(store)
microsalt.add_command(store_available)
microsalt.add_command(resolve_compression)


@microsalt.command()
@OPTION_TICKET
@OPTION_SAMPLE
@OPTION_DRY_RUN
@ARGUMENT_UNIQUE_IDENTIFIER
@click.pass_obj
def link(context: CGConfig, ticket: bool, sample: bool, unique_id: str, dry_run: bool) -> None:
    """Link microbial FASTQ files to dedicated analysis folder for a given case, ticket or sample"""
    if dry_run:
        return
    analysis_api: MicrosaltAnalysisAPI = context.meta_apis["analysis_api"]
    case_id, sample_id = analysis_api.resolve_case_sample_id(
        sample=sample, ticket=ticket, unique_id=unique_id
    )
    analysis_api.link_fastq_files(
        case_id=case_id,
        sample_id=sample_id,
    )


@microsalt.command("config-case")
@OPTION_DRY_RUN
@OPTION_TICKET
@OPTION_SAMPLE
@ARGUMENT_UNIQUE_IDENTIFIER
@click.pass_obj
def config_case(
    context: CGConfig, dry_run: bool, ticket: bool, sample: bool, unique_id: str
) -> None:
    """Create a config file for a case or a sample analysis in microSALT"""

    analysis_api: MicrosaltAnalysisAPI = context.meta_apis["analysis_api"]
    case_id, sample_id = analysis_api.resolve_case_sample_id(
        sample=sample, ticket=ticket, unique_id=unique_id
    )
    sample_objs: List[Sample] = analysis_api.get_samples(case_id=case_id, sample_id=sample_id)

    if not sample_objs:
        LOG.error("No sample found for that ticket/sample_id")
        raise click.Abort

    parameters: List[dict] = [analysis_api.get_parameters(sample_obj) for sample_obj in sample_objs]
    filename: str = sample_id or case_id
    config_case_path: Path = analysis_api.get_config_path(filename=filename)
    if dry_run:
        click.echo(
            WriteStream.write_stream_from_content(content=parameters, file_format=FileFormat.JSON)
        )
        return
    WriteFile.write_file_from_content(
        content=parameters, file_format=FileFormat.JSON, file_path=config_case_path
    )
    LOG.info("Saved config %s", config_case_path)


@microsalt.command()
@OPTION_DRY_RUN
@OPTION_TICKET
@OPTION_SAMPLE
@ARGUMENT_UNIQUE_IDENTIFIER
@click.option(
    "-c",
    "--config-case",
    "config_case_path",
    required=False,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help="optionally change the config-case",
)
@click.pass_obj
def run(
    context: CGConfig,
    dry_run: bool,
    config_case_path: click.Path,
    ticket: bool,
    sample: bool,
    unique_id: Any,
) -> None:
    """Start microSALT workflow by providing case, ticket or sample id"""

    analysis_api: MicrosaltAnalysisAPI = context.meta_apis["analysis_api"]
    case_id, sample_id = analysis_api.resolve_case_sample_id(
        sample=sample, ticket=ticket, unique_id=unique_id
    )
    fastq_path: Path = analysis_api.get_case_fastq_path(case_id=case_id)
    if not config_case_path:
        filename = sample_id or case_id
        config_case_path: Path = analysis_api.get_config_path(filename=filename)

    if not sample_id:
        analyse_command = [
            "analyse",
            config_case_path.absolute().as_posix(),
            "--input",
            fastq_path.absolute().as_posix(),
        ]
    else:
        analyse_command = [
            "analyse",
            config_case_path.absolute().as_posix(),
            "--input",
            Path(fastq_path, sample_id).absolute().as_posix(),
        ]

    if sample_id or dry_run:
        analysis_api.process.run_command(parameters=analyse_command, dry_run=dry_run)
        return
    try:
        analysis_api.add_pending_trailblazer_analysis(case_id=case_id)
    except Exception as error:
        LOG.warning(
            "Trailblazer warning: Could not track analysis progress for case %s! %s",
            case_id,
            error.__class__.__name__,
        )
    try:
        analysis_api.set_statusdb_action(case_id=case_id, action="running")
        analysis_api.process.run_command(parameters=analyse_command, dry_run=dry_run)
    except:
        LOG.error("Failed to run analysis!")
        analysis_api.set_statusdb_action(case_id=case_id, action=None)
        raise


@microsalt.command()
@ARGUMENT_UNIQUE_IDENTIFIER
@OPTION_DRY_RUN
@OPTION_TICKET
@OPTION_SAMPLE
@click.pass_context
def start(
    context: click.Context, ticket: bool, sample: bool, unique_id: str, dry_run: bool
) -> None:
    """Start whole microSALT workflow by providing case, ticket or sample id"""
    LOG.info("Starting Microsalt workflow for %s", unique_id)

    context.invoke(link, ticket=ticket, sample=sample, unique_id=unique_id, dry_run=dry_run)
    context.invoke(config_case, ticket=ticket, sample=sample, unique_id=unique_id, dry_run=dry_run)
    context.invoke(run, ticket=ticket, sample=sample, unique_id=unique_id, dry_run=dry_run)


@microsalt.command("start-available")
@OPTION_DRY_RUN
@click.pass_context
def start_available(context: click.Context, dry_run: bool = False):
    """Start full analysis workflow for all cases ready for analysis"""

    analysis_api: MicrosaltAnalysisAPI = context.obj.meta_apis["analysis_api"]

    exit_code: int = EXIT_SUCCESS
    for case_obj in analysis_api.get_cases_to_analyze():
        try:
            context.invoke(start, unique_id=case_obj.internal_id, dry_run=dry_run)
        except CgError as error:
            LOG.error(error)
            exit_code = EXIT_FAIL
        except Exception as error:
            LOG.error(f"Unspecified error occurred: {error}")
            exit_code = EXIT_FAIL
    if exit_code:
        raise click.Abort


@microsalt.command("upload-analysis-vogue")
@OPTION_DRY_RUN
@ARGUMENT_UNIQUE_IDENTIFIER
@click.pass_obj
def upload_analysis_vogue(context: CGConfig, unique_id: str, dry_run: bool) -> None:
    """Upload the trending report for latest analysis of given case_id to Vogue"""

    analysis_api: MicrosaltAnalysisAPI = context.meta_apis["analysis_api"]
    case_obj = analysis_api.status_db.get_case_by_internal_id(internal_id=unique_id)
    if not case_obj or not case_obj.analyses:
        LOG.error("No analysis available for %s", unique_id)
        raise click.Abort

    samples_string = ",".join(str(link_obj.sample.internal_id) for link_obj in case_obj.links)
    microsalt_version: str = analysis_api.get_pipeline_version(case_id=case_obj.internal_id)

    if dry_run:
        LOG.info(
            "Would have loaded case %s, with samples %s, analyzed with pipeline version %s",
            unique_id,
            samples_string,
            microsalt_version,
        )
        return

    analysis_result_file: Optional[File] = analysis_api.housekeeper_api.get_files(
        bundle=unique_id, tags=["vogue"]
    ).first()
    if not analysis_result_file:
        LOG.error("Vogue upload file not found in Housekeeper for case %s", unique_id)
        raise click.Abort

    vogue_load_args = {
        "samples": samples_string,
        "analysis_result_file": analysis_result_file.full_path,
        "analysis_case_name": unique_id,
        "analysis_type": "microsalt",
        "analysis_workflow_name": "microsalt",
        "analysis_workflow_version": microsalt_version,
        "case_analysis_type": "microsalt",
    }
    analysis_api.vogue_api.load_bioinfo_raw(load_bioinfo_inputs=vogue_load_args)
    analysis_api.vogue_api.load_bioinfo_process(
        load_bioinfo_inputs=vogue_load_args, cleanup_flag=False
    )
    analysis_api.vogue_api.load_bioinfo_sample(load_bioinfo_inputs=vogue_load_args)
    case_obj.analyses[0].uploaded_at = dt.datetime.now()
    analysis_api.status_db.session.commit()
    LOG.info("Successfully uploaded latest analysis data for case %s to Vogue!", unique_id)


@microsalt.command("upload-latest-analyses-vogue")
@OPTION_DRY_RUN
@click.pass_context
def upload_vogue_latest(context: click.Context, dry_run: bool) -> None:
    """Upload the trending reports for all un-uploaded latest analyses to Vogue"""

    EXIT_CODE: int = EXIT_SUCCESS
    analysis_api: MicrosaltAnalysisAPI = context.obj.meta_apis["analysis_api"]
    latest_analyses: List[
        Analysis
    ] = analysis_api.status_db.get_latest_analysis_to_upload_for_pipeline(
        pipeline=Pipeline.MICROSALT
    )
    if not latest_analyses:
        LOG.info("No new analyses to upload to Vogue!")
        return

    for analysis in latest_analyses:
        case_internal_id: str = analysis.family.internal_id if analysis.family else None
        try:
            context.invoke(upload_analysis_vogue, unique_id=case_internal_id, dry_run=dry_run)
        except Exception as error:
            LOG.error(
                "Could not upload data for %s to vogue, exception %s",
                case_internal_id,
                error.__class__.__name__,
            )
            EXIT_CODE: int = EXIT_FAIL

    if EXIT_CODE:
        raise click.Abort


@microsalt.command("qc-microsalt")
@ARGUMENT_UNIQUE_IDENTIFIER
@click.pass_context
def qc_microsalt(context: click.Context, unique_id: str) -> None:
    """Perform QC on a microsalt case."""
    analysis_api: MicrosaltAnalysisAPI = context.obj.meta_apis["analysis_api"]
    try:
        analysis_api.microsalt_qc(
            case_id=unique_id,
            run_dir_path=analysis_api.get_latest_case_path(case_id=unique_id),
            lims_project=analysis_api.get_project(
                analysis_api.status_db.get_case_by_internal_id(internal_id=unique_id)
                .samples[0]
                .internal_id
            ),
        )
    except IndexError:
        LOG.error(f"No existing analysis directories found for case {unique_id}.")
