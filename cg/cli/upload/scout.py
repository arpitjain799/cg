"""Code for uploading to scout via CLI"""
import logging
from pathlib import Path
from typing import Dict, Optional

import click
from housekeeper.store.models import File, Version

from cg.apps.housekeeper.hk import HousekeeperAPI
from cg.apps.scout.scoutapi import ScoutAPI
from cg.cli.upload.utils import suggest_cases_to_upload
from cg.constants import Pipeline
from cg.constants.constants import FileFormat
from cg.exc import CgDataError, ScoutUploadError
from cg.io.controller import WriteStream
from cg.meta.upload.upload_api import UploadAPI
from cg.meta.upload.scout.uploadscoutapi import UploadScoutAPI
from cg.meta.workflow.balsamic import BalsamicAnalysisAPI
from cg.meta.workflow.balsamic_umi import BalsamicUmiAnalysisAPI
from cg.meta.workflow.mip_dna import MipDNAAnalysisAPI
from cg.meta.workflow.mip_rna import MipRNAAnalysisAPI
from cg.meta.workflow.rnafusion import RnafusionAnalysisAPI
from cg.models.cg_config import CGConfig
from cg.models.scout.scout_load_config import ScoutLoadConfig
from cg.store import Store
from cg.store.models import Family


LOG = logging.getLogger(__name__)


@click.command()
@click.option(
    "-r",
    "--re-upload",
    is_flag=True,
    help="re-upload existing analysis",
)
@click.option("-p", "--print", "print_console", is_flag=True, help="print config values")
@click.argument("case_id", required=False)
@click.pass_context
def scout(context, re_upload: bool, print_console: bool, case_id: str):
    """Upload variants from analysis to Scout."""
    status_db: Store = context.obj.status_db

    LOG.info("----------------- SCOUT -----------------------")

    if not case_id:
        suggest_cases_to_upload(status_db=status_db)
        return

    context.invoke(
        create_scout_load_config, case_id=case_id, print_console=print_console, re_upload=re_upload
    )
    if not print_console:
        context.invoke(upload_case_to_scout, case_id=case_id, re_upload=re_upload)


@click.command(name="create-scout-load-config")
@click.argument("case-id")
@click.option("-p", "--print", "print_console", is_flag=True, help="Only print config")
@click.option("-r", "--re-upload", is_flag=True, help="Overwrite existing load configs")
@click.pass_obj
def create_scout_load_config(context: CGConfig, case_id: str, print_console: bool, re_upload: bool):
    """Create a load config for a case in scout and add it to housekeeper"""

    status_db: Store = context.status_db

    LOG.info("Fetching family object")
    case_obj: Family = status_db.get_case_by_internal_id(internal_id=case_id)

    if not case_obj.analyses:
        LOG.warning("Could not find analyses for %s", case_id)
        raise click.Abort

    context.meta_apis["upload_api"]: UploadAPI = get_upload_api(cg_config=context, case=case_obj)

    scout_upload_api: UploadScoutAPI = context.meta_apis["upload_api"].scout_upload_api

    LOG.info("----------------- CREATE CONFIG -----------------------")
    LOG.info("Create load config")
    try:
        scout_load_config: ScoutLoadConfig = scout_upload_api.generate_config(case_obj.analyses[0])
    except SyntaxError as error:
        LOG.warning("%s", error)
        raise click.Abort from error
    LOG.info("Found load config %s", scout_load_config)
    root_dir: str = context.meta_apis["upload_api"].analysis_api.root
    LOG.info("Set root dir to %s", root_dir)
    file_path: Path = Path(root_dir, case_id, "scout_load.yaml")

    if print_console:
        click.echo(
            WriteStream.write_stream_from_content(
                content=scout_load_config.dict(exclude_none=True), file_format=FileFormat.YAML
            )
        )
        LOG.info("Would save file to %s", file_path)
        return

    if file_path.exists():
        LOG.warning("Scout load config %s already exists", file_path)
        if re_upload:
            LOG.info("Deleting old load config")
            file_path.unlink()
        else:
            LOG.info(
                "You might remove the file and try again, consider that you might also have it in housekeeper"
            )
            raise click.Abort
    LOG.info("Saving config file to disc")
    scout_upload_api.save_config_file(upload_config=scout_load_config, file_path=file_path)

    try:
        LOG.info("Add config file to housekeeper")
        scout_upload_api.add_scout_config_to_hk(
            config_file_path=file_path, case_id=case_id, delete=re_upload
        )
    except FileExistsError as error:
        LOG.warning("%s, consider removing the file from housekeeper and try again", str(error))
        raise click.Abort


@click.command(name="upload-case-to-scout")
@click.option(
    "-r",
    "--re-upload",
    is_flag=True,
    help="re-upload existing analysis",
)
@click.option("--dry-run", is_flag=True)
@click.argument("case_id")
@click.pass_obj
def upload_case_to_scout(context: CGConfig, re_upload: bool, dry_run: bool, case_id: str):
    """Upload variants and case from analysis to Scout."""

    LOG.info("----------------- UPLOAD -----------------------")

    housekeeper_api: HousekeeperAPI = context.housekeeper_api
    scout_api: ScoutAPI = context.scout_api

    tag_name: str = UploadScoutAPI.get_load_config_tag()
    version: Version = housekeeper_api.last_version(bundle=case_id)
    scout_config_file: Optional[File] = housekeeper_api.get_latest_file_from_version(
        version=version, tags={tag_name}
    )

    if scout_config_file is None:
        raise FileNotFoundError(f"No scout load config was found in housekeeper for {case_id}")

    LOG.info(f"Uploading case {case_id} to scout")

    if not dry_run:
        scout_api.upload(scout_load_config=scout_config_file.full_path, force=re_upload)

    LOG.info(f"Uploaded to scout using load config {scout_config_file.full_path}")
    LOG.info("Case loaded successfully to Scout")


@click.command(name="rna-to-scout")
@click.option("--dry-run", is_flag=True)
@click.option("-r", "--research", is_flag=True, help="Upload research report instead of clinical")
@click.option(
    "-u",
    "--update-fusion-report",
    is_flag=True,
    help="re-upload existing fusion report",
)
@click.argument("case_id")
@click.pass_context
def upload_rna_to_scout(
    context, case_id: str, dry_run: bool, update_fusion_report: bool, research: bool
) -> int:
    """Upload an RNA case's gene fusion report and junction splice files for all samples connect via subject_id

    Args:
        case_id                 (string):       RNA case identifier
        dry_run                 (bool):         Skip uploading
        research                (bool):         Upload research report instead of clinical
        update_fusion_report    (bool):         Overwrite existing fusion report
    Returns:

    """

    LOG.info("----------------- UPLOAD RNA TO SCOUT -----------------------")

    result: int = context.invoke(
        upload_rna_fusion_report_to_scout,
        case_id=case_id,
        dry_run=dry_run,
        research=research,
        update=update_fusion_report,
    )
    if result == 0:
        result = context.invoke(upload_rna_junctions_to_scout, case_id=case_id, dry_run=dry_run)
    return result


@click.command(name="rna-fusion-report-to-scout")
@click.option("--dry-run", is_flag=True)
@click.option("--research", is_flag=True)
@click.option(
    "-u",
    "--update",
    is_flag=True,
    help="Overwrite existing report",
)
@click.argument("case_id")
@click.pass_obj
def upload_rna_fusion_report_to_scout(
    context: CGConfig, dry_run: bool, case_id: str, update: bool, research: bool
) -> int:
    """Upload fusion report file for a case to Scout.
    This can also be run as
    `housekeeper get file -V --tag fusion --tag pdf --tag clinical/research <case_id>`
    `scout load gene-fusion-report [-r] <case_id> <path/to/research_gene_fusion_report.pdf>`

    Args:
        dry_run     (bool):         Skip uploading
        case_id     (string):       RNA case identifier
        research    (bool):         Upload research report instead of clinical
        update      (bool):         Overwrite existing report
    Returns:

    """
    LOG.info("----------------- UPLOAD RNA FUSION REPORT TO SCOUT -----------------------")

    scout_upload_api: UploadScoutAPI = context.meta_apis["upload_api"].scout_upload_api
    try:
        scout_upload_api.upload_fusion_report_to_scout(
            dry_run=dry_run, research=research, case_id=case_id, update=update
        )
    except (CgDataError, ScoutUploadError) as error:
        LOG.error(error)
        return 1
    return 0


@click.command(name="rna-junctions-to-scout")
@click.option("--dry-run", is_flag=True)
@click.argument("case_id")
@click.pass_obj
def upload_rna_junctions_to_scout(context: CGConfig, case_id: str, dry_run: bool) -> int:
    """Upload RNA junctions splice files to Scout.
        This can also be run as
        `housekeeper get file -V --tag junction --tag bed <sample_id>`
        `scout update individual -c <case_id> -n <customer_sample_id> splice_junctions_bed <path/to/junction_file.bed>`
        `housekeeper get file -V --tag coverage --tag bigwig <sample_id>`
        scout update individual -c <case_id> -n <customer_sample_id> rna_coverage_bigwig <path/to/coverage_file.bigWig>
    `   ```

        Args:
            dry_run     (bool):         Skip uploading
            case_id     (string):       RNA case identifier
        Returns:

    """
    LOG.info("----------------- UPLOAD RNA JUNCTIONS TO SCOUT -----------------------")

    scout_upload_api: UploadScoutAPI = context.meta_apis["upload_api"].scout_upload_api
    try:
        scout_upload_api.upload_rna_junctions_to_scout(dry_run=dry_run, case_id=case_id)
    except (CgDataError, ScoutUploadError) as error:
        LOG.error(error)
        return 1
    return 0


def get_upload_api(case: Family, cg_config: CGConfig) -> UploadAPI:
    """Return the upload API based on the data analysis type"""

    analysis_apis: Dict[Pipeline, UploadAPI] = {
        Pipeline.BALSAMIC: BalsamicAnalysisAPI,
        Pipeline.BALSAMIC_UMI: BalsamicUmiAnalysisAPI,
        Pipeline.MIP_RNA: MipRNAAnalysisAPI,
        Pipeline.MIP_DNA: MipDNAAnalysisAPI,
        Pipeline.RNAFUSION: RnafusionAnalysisAPI,
    }

    return UploadAPI(
        config=cg_config, analysis_api=analysis_apis.get(case.data_analysis)(cg_config)
    )
