"""MIP-RNA upload API."""

import logging
import datetime as dt

import click

from cg.cli.upload.scout import upload_rna_to_scout
from cg.cli.upload.clinical_delivery import clinical_delivery
from cg.constants import DataDelivery
from cg.meta.workflow.mip_rna import MipRNAAnalysisAPI
from cg.meta.upload.upload_api import UploadAPI
from cg.models.cg_config import CGConfig
from cg.store.models import Family, Analysis

LOG = logging.getLogger(__name__)


class MipRNAUploadAPI(UploadAPI):
    """MIP-RNA upload API."""

    def __init__(self, config: CGConfig):
        self.analysis_api: MipRNAAnalysisAPI = MipRNAAnalysisAPI(config)
        super().__init__(config=config, analysis_api=self.analysis_api)

    def upload(self, ctx: click.Context, case_obj: Family, restart: bool) -> None:
        """Uploads MIP-RNA analysis data and files."""

        analysis_obj: Analysis = case_obj.analyses[0]
        self.update_upload_started_at(analysis=analysis_obj)

        # Clinical delivery upload
        ctx.invoke(clinical_delivery, case_id=case_obj.internal_id)

        # Scout specific upload
        if DataDelivery.SCOUT in case_obj.data_delivery:
            ctx.invoke(upload_rna_to_scout, case_id=case_obj.internal_id)
        else:
            LOG.warning(
                f"There is nothing to upload to Scout for case {case_obj.internal_id} and "
                f"the specified data delivery ({case_obj.data_delivery})"
            )

        LOG.info(
            f"Upload of case {case_obj.internal_id} was successful. Setting uploaded at to {dt.datetime.now()}"
        )
        self.update_uploaded_at(analysis_obj)