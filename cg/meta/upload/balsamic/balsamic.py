"""Balsamic upload API"""

import logging

import click
from cg.cli.upload.scout import scout
from cg.constants import DataDelivery
from cg.meta.workflow.balsamic import BalsamicAnalysisAPI
from cg.models.cg_config import CGConfig
from cg.meta.upload.upload_api import UploadAPI
from cg.store import models

LOG = logging.getLogger(__name__)


class BalsamicUploadAPI(UploadAPI):
    """Balsamic upload API"""

    def __init__(self, config: CGConfig):
        self.analysis_api: BalsamicAnalysisAPI = BalsamicAnalysisAPI(config)
        super().__init__(config=config, analysis_api=self.analysis_api)

    def upload(self, ctx: click.Context, case_obj: models.Family, restart: bool) -> None:
        """Uploads BALSAMIC analysis data and files"""

        analysis_obj: models.Analysis = case_obj.analyses[0]

        # Scout specific upload
        if DataDelivery.SCOUT in case_obj.data_delivery:
            self.update_upload_started_at(analysis_obj)
            ctx.invoke(scout, case_id=case_obj.internal_id, re_upload=restart)
            self.update_uploaded_at(analysis_obj)
        else:
            LOG.warning(
                f"There is nothing to upload for case {case_obj.internal_id} and "
                f"the specified data delivery ({case_obj.data_delivery})"
            )
            ctx.abort()