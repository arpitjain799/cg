"""Functions that handle files in the context of scout uploading"""
import logging
from typing import Optional, Set

import requests
from cg.apps.housekeeper.hk import HousekeeperAPI
from cg.apps.lims import LimsAPI
from cg.meta.upload.scout.hk_tags import CaseTags, SampleTags
from cg.meta.upload.scout.scout_load_config import ScoutIndividual, ScoutLoadConfig
from cg.store import models
from housekeeper.store import models as hk_models

LOG = logging.getLogger(__name__)

# Maps keys that are used in scout load config on tags that are used in scout


class ScoutConfigBuilder:
    """Base class for handling files that should be included in Scout upload"""

    def __init__(
        self, hk_version_obj: hk_models.Version, analysis_obj: models.Analysis, lims_api: LimsAPI
    ):
        self.hk_version_obj: hk_models.Version = hk_version_obj
        self.analysis_obj: models.Analysis = analysis_obj
        self.lims_api: LimsAPI = lims_api
        self.case_tags: CaseTags
        self.sample_tags: SampleTags
        self.load_config: ScoutLoadConfig = ScoutLoadConfig()

    def add_mandatory_info_to_load_config(self) -> None:
        """Add the mandatory common information to a scout load config object"""
        self.load_config.analysis_date = self.analysis_obj.completed_at
        self.load_config.default_gene_panels = self.analysis_obj.family.panels
        self.load_config.family = self.analysis_obj.family.internal_id
        self.load_config.family_name = self.analysis_obj.family.name
        self.load_config.owner = self.analysis_obj.family.customer.internal_id

    def add_mandatory_sample_info(
        self,
        config_sample: ScoutIndividual,
        db_sample: models.FamilySample,
    ) -> None:
        """Add the information to a sample that is common for different analysis types"""
        sample_id: str = db_sample.sample.internal_id
        LOG.info("Building sample %s", sample_id)
        lims_sample = dict()
        try:
            lims_sample = self.lims_api.sample(sample_id) or {}
        except requests.exceptions.HTTPError as ex:
            LOG.info("Could not fetch sample %s from LIMS: %s", sample_id, ex)

        config_sample.sample_id = sample_id
        config_sample.sex = db_sample.sample.sex
        config_sample.phenotype = db_sample.status
        config_sample.analysis_type = db_sample.sample.application_version.application.analysis_type
        config_sample.sample_name = db_sample.sample.name
        config_sample.tissue_type = lims_sample.get("source", "unknown")

        self.include_sample_alignment_file(config_sample=config_sample)
        self.include_sample_files(config_sample=config_sample)

    def build_config_sample(self, db_sample: models.FamilySample) -> ScoutIndividual:
        """Build a sample for the scout load config"""
        raise NotImplementedError

    def build_load_config(self) -> ScoutLoadConfig:
        """Build a load config for uploading a case to scout"""
        raise NotImplementedError

    def include_sample_files(self, config_sample: ScoutIndividual) -> None:
        """Include all files that are used on sample level in Scout"""
        raise NotImplementedError

    def include_case_files(self) -> None:
        """Include all files that are used on case level in scout"""
        raise NotImplementedError

    def include_multiqc_report(self) -> None:
        LOG.info("Include MultiQC report to case")
        self.load_config.multiqc = self.fetch_file_from_hk(self.case_tags.multiqc_report)

    def include_delivery_report(self) -> None:
        LOG.info("Include delivery report to case")
        self.load_config.delivery_report = self.fetch_file_from_hk(self.case_tags.delivery_report)

    def include_sample_alignment_file(self, config_sample: ScoutIndividual) -> None:
        """Include the alignment file for a sample

        First add the bam.
        Cram is preferred so overwrite if found
        """
        sample_id: str = config_sample.sample_id
        config_sample.alignment_path = self.fetch_sample_file(
            hk_tags=self.sample_tags.bam_file, sample_id=sample_id
        )

        config_sample.alignment_path = self.fetch_sample_file(
            hk_tags=self.sample_tags.alignment_file, sample_id=sample_id
        )

    def fetch_sample_file(self, hk_tags: Set[str], sample_id: str) -> Optional[str]:
        """Fetch a file that is specific for a individual from housekeeper"""
        tags: set = hk_tags.copy()
        tags.add(sample_id)
        return self.fetch_file_from_hk(hk_tags=tags)

    def fetch_file_from_hk(self, hk_tags: Set[str]) -> Optional[str]:
        """Fetch a file from housekeeper and return the path as a string.
        If file does not exist return None
        """
        LOG.info("Fetch file with tags %s", hk_tags)
        if not hk_tags:
            LOG.debug("No tags provided, skipping")
            return None
        hk_file: Optional[hk_models.File] = HousekeeperAPI.fetch_file_from_version(
            version_obj=self.hk_version_obj, tags=hk_tags
        )
        if hk_file is None:
            return hk_file
        return hk_file.full_path
