"""Code for uploading delivery report from the CLI"""
import datetime as dt
import logging

import click

from cg.apps import hk, scoutapi

from .utils import _suggest_cases_delivery_report

LOG = logging.getLogger(__name__)


@click.command("delivery-reports")
@click.option(
    "-p", "--print", "print_console", is_flag=True, help="print list to console"
)
@click.pass_context
def delivery_reports(context, print_console):
    """Generate a delivery reports for all cases that need one"""

    click.echo(
        click.style("----------------- DELIVERY REPORTS ------------------------")
    )

    for analysis_obj in context.obj["status"].analyses_to_delivery_report():
        LOG.info(
            "uploading delivery report for family: %s", analysis_obj.family.internal_id
        )
        try:
            context.invoke(
                delivery_report,
                family_id=analysis_obj.family.internal_id,
                print_console=print_console,
            )
        except Exception:
            LOG.error(
                "uploading delivery report failed for family: %s",
                analysis_obj.family.internal_id,
            )


@click.command("delivery-report")
@click.argument("family_id", required=False)
@click.option(
    "-p", "--print", "print_console", is_flag=True, help="print report to console"
)
@click.pass_context
def delivery_report(context, family_id, print_console):
    """Generates a delivery report for a case and uploads it to housekeeper and scout

    The report contains data from several sources:

    status-db:
        family
        customer_obj
        application_objs
        accredited
        panels
        samples
        sample.id
        sample.status
        sample.ticket
        sample.million_read_pairs
        sample.prep_date
        sample.received
        sample.sequencing_date
        sample.delivery_date

    lims:
        sample.name
        sample.sex
        sample.source
        sample.application
        sample.prep_method
        sample.sequencing_method
        sample.delivery_method


    trailblazer:
        sample.mapped_reads
        sample.duplicates
        sample.analysis_sex
        mip_version
        genome_build

    chanjo:
        sample.target_coverage
        sample.target_completeness

    scout:
        panel-genes

    calculated:
        today
        sample.processing_time

    """

    click.echo(click.style("----------------- DELIVERY_REPORT -------------"))

    def _add_delivery_report_to_hk(
        delivery_report_file, hk_api: hk.HousekeeperAPI, family_id
    ):
        delivery_report_tag_name = "delivery-report"
        version_obj = hk_api.last_version(family_id)
        uploaded_delivery_report_files = hk_api.get_files(
            bundle=family_id, tags=[delivery_report_tag_name], version=version_obj.id
        )
        number_of_delivery_reports = len(uploaded_delivery_report_files.all())
        is_bundle_missing_delivery_report = number_of_delivery_reports == 0

        if is_bundle_missing_delivery_report:
            file_obj = hk_api.add_file(
                delivery_report_file.name, version_obj, delivery_report_tag_name
            )
            hk_api.include_file(file_obj, version_obj)
            hk_api.add_commit(file_obj)
            return file_obj

        return None

    def _update_delivery_report_date(status_api, case_id):
        family_obj = status_api.family(case_id)
        analysis_obj = family_obj.analyses[0]
        analysis_obj.delivery_report_created_at = dt.datetime.now()
        status_api.commit()

    report_api = context.obj["report_api"]

    if not family_id:
        _suggest_cases_delivery_report(context)
        context.abort()

    if print_console:
        delivery_report_html = report_api.create_delivery_report(family_id)
        click.echo(delivery_report_html)
        return

    tb_api = context.obj["tb_api"]
    status_api = context.obj["status"]
    delivery_report_file = report_api.create_delivery_report_file(
        family_id, file_path=tb_api.get_family_root_dir(family_id)
    )
    hk_api = context.obj["housekeeper_api"]
    added_file = _add_delivery_report_to_hk(delivery_report_file, hk_api, family_id)

    if added_file:
        click.echo(click.style("uploaded to housekeeper", fg="green"))
    else:
        click.echo(click.style("already uploaded to housekeeper, skipping"))

    context.invoke(delivery_report_to_scout, case_id=family_id)
    _update_delivery_report_date(status_api, family_id)


@click.command("delivery-report-to-scout")
@click.argument("case_id", required=False)
@click.option(
    "-d",
    "--dry-run",
    "dry_run",
    is_flag=True,
    help="run command without uploading to " "scout",
)
@click.pass_context
def delivery_report_to_scout(context, case_id, dry_run):
    """Fetches an delivery-report from housekeeper and uploads it to scout"""

    def _add_delivery_report_to_scout(context, path, case_id):
        scout_api = scoutapi.ScoutAPI(context.obj)
        scout_api.upload_delivery_report(path, case_id, update=True)

    def _get_delivery_report_from_hk(hk_api: hk.HousekeeperAPI, family_id):
        delivery_report_tag_name = "delivery-report"
        version_obj = hk_api.last_version(family_id)
        uploaded_delivery_report_files = hk_api.get_files(
            bundle=family_id, tags=[delivery_report_tag_name], version=version_obj.id
        )

        if uploaded_delivery_report_files.count() == 0:
            raise FileNotFoundError(
                f"No delivery report was found in housekeeper for {family_id}"
            )

        return uploaded_delivery_report_files[0].full_path

    if not case_id:
        _suggest_cases_delivery_report(context)
        context.abort()

    hk_api = context.obj["housekeeper_api"]
    report = _get_delivery_report_from_hk(hk_api, case_id)

    LOG.info("uploading delivery report %s to scout for case: %s", report, case_id)
    if not dry_run:
        _add_delivery_report_to_scout(context, report, case_id)
    click.echo(click.style("uploaded to scout", fg="green"))
