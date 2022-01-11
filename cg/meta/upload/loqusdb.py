import logging
from pathlib import Path
from typing import Optional

from cg.constants.loqus_upload import ObservationAnalysisTag
from cg.meta.meta import MetaAPI
from cg.models.cg_config import CGConfig
from typing_extensions import Literal

from housekeeper.store.models import File

LOG = logging.getLogger(__name__)


class LoqusDBAPI(MetaAPI):
    def __init__(self, config: CGConfig, dbtype: Literal["loqusdb", "loqusdb_wes"] = "loqusdb"):
        self.upload_uri = config.__getattribute__(dbtype).get("uri")
        super().__init__(config=config)

    def get_case_profile_path(self, case_id: str) -> Path:
        file_obj: File = self.housekeeper_api.find_file_in_latest_version(
            case_id=case_id, tags=[ObservationAnalysisTag.CHECK_PROFILE_GBCF]
        )
        if not file_obj:
            LOG.error(f"Profile file path not found for case {case_id}")
            raise Exception
        file_path: Path = Path(file_obj.full_path)
        if not file_path.exists():
            raise Exception
        return file_path

    def get_case_sv_path(self, case_id: str) -> Optional[Path]:
        file_obj: File = self.housekeeper_api.find_file_in_latest_version(
            case_id=case_id, tags=[ObservationAnalysisTag.SV_VARIANTS]
        )
        if not file_obj:
            LOG.info(f"SV file path not found for case {case_id}")
            return
        file_path: Path = Path(file_obj.full_path)
        if not file_path.exists():
            LOG.info(f"SV file path {file_path} does not exist for case {case_id}")
            return
        return file_path

    def get_case_snv_path(self, case_id: str) -> Path:
        file_obj: File = self.housekeeper_api.find_file_in_latest_version(
            case_id=case_id, tags=[ObservationAnalysisTag.SNV_VARIANTS]
        )
        if not file_obj:
            LOG.error(f"SNV file path not found for case {case_id}")
            raise Exception
        file_path: Path = Path(file_obj.full_path)
        if not file_path.exists():
            raise Exception
        return file_path

    def generate_upload_url(self):
        pass

    def generate_delete_url(self):
        pass

    def delete_case(self):
        pass

    def get_case(self):
        pass
