import logging

from cg.apps.lims import LimsAPI
from cg.constants.scout_upload import BALSAMIC_CASE_TAGS, BALSAMIC_SAMPLE_TAGS
from cg.meta.upload.scout.hk_tags import CaseTags, SampleTags
from cg.meta.upload.scout.scout_config_builder import ScoutConfigBuilder
from cg.meta.upload.scout.scout_load_config import BalsamicLoadConfig, ScoutBalsamicIndividual
from cg.meta.workflow.balsamic import BalsamicAnalysisAPI
from cg.store import models
from housekeeper.store import models as hk_models
from typing_extensions import Literal

LOG = logging.getLogger(__name__)


class BalsamicConfigBuilder(ScoutConfigBuilder):
    def __init__(
        self, hk_version_obj: hk_models.Version, analysis_obj: models.Analysis, lims_api: LimsAPI
    ):
        super().__init__(
            hk_version_obj=hk_version_obj, analysis_obj=analysis_obj, lims_api=lims_api
        )
        self.case_tags: CaseTags = CaseTags(**BALSAMIC_CASE_TAGS)
        self.sample_tags: SampleTags = SampleTags(**BALSAMIC_SAMPLE_TAGS)
        self.load_config: BalsamicLoadConfig = BalsamicLoadConfig(track="cancer")

    def include_case_files(self):
        LOG.info("Including BALSAMIC specific case level files")
        self.load_config.vcf_cancer = self.fetch_file_from_hk(self.case_tags.snv_vcf)
        self.load_config.vcf_cancer_sv = self.fetch_file_from_hk(self.case_tags.sv_vcf)
        self.include_multiqc_report()

    def include_sample_files(self, config_sample: ScoutBalsamicIndividual):
        LOG.info("Including BALSAMIC specific sample level files")

    def build_config_sample(self, db_sample: models.FamilySample) -> ScoutBalsamicIndividual:
        """Build a sample with balsamic specific information"""
        config_sample = ScoutBalsamicIndividual()

        self.add_mandatory_sample_info(config_sample=config_sample, db_sample=db_sample)
        if BalsamicAnalysisAPI.get_sample_type(db_sample) == "tumor":
            config_sample.phenotype = "affected"
        else:
            config_sample.phenotype = "unaffected"

        analysis_type: Literal["wgs", "wes", "tgs"] = BalsamicAnalysisAPI.get_application_type(
            db_sample
        )
        if analysis_type == "tgs":
            analysis_type = "panel"
        config_sample.analysis_type = analysis_type
        return config_sample

    def build_load_config(self) -> None:
        LOG.info("Build load config for balsamic case")
        self.add_mandatory_info_to_load_config()
        self.load_config.human_genome_build = "37"
        self.load_config.rank_score_threshold = 0

        self.include_case_files()

        LOG.info("Building samples")
        db_sample: models.FamilySample

        for db_sample in self.analysis_obj.family.links:
            self.load_config.samples.append(self.build_config_sample(db_sample=db_sample))