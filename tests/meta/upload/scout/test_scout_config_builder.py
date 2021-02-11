"""Tests for the file handlers"""
from typing import Optional

from cg.meta.upload.scout.balsamic_config_builder import BalsamicConfigBuilder
from cg.meta.upload.scout.hk_tags import CaseTags, SampleTags
from cg.meta.upload.scout.mip_config_builder import MipConfigBuilder
from cg.meta.upload.scout.scout_load_config import (
    BalsamicLoadConfig,
    MipLoadConfig,
    ScoutLoadConfig,
    ScoutMipIndividual,
)
from cg.store import models
from housekeeper.store import models as hk_models
from tests.mocks.limsmock import MockLimsAPI
from tests.mocks.madeline import MockMadelineAPI

from .conftest import MockAnalysis


def test_mip_config_builder(
    hk_version_obj: hk_models.Version,
    mip_analysis_obj: models.Analysis,
    lims_api: MockLimsAPI,
    mip_analysis_api: MockAnalysis,
    madeline_api: MockMadelineAPI,
):
    # GIVEN a mip file handler

    # WHEN instantiating
    config_builder = MipConfigBuilder(
        hk_version_obj=hk_version_obj,
        analysis_obj=mip_analysis_obj,
        lims_api=lims_api,
        mip_analysis_api=mip_analysis_api,
        madeline_api=madeline_api,
    )

    # THEN assert that the correct case tags was used
    assert isinstance(config_builder.case_tags, CaseTags)


def test_balsamic_config_builder(
    hk_version_obj: hk_models.Version, balsamic_analysis_obj: models.Analysis, lims_api: MockLimsAPI
):
    # GIVEN a balsamic file handler

    # WHEN instantiating
    file_handler = BalsamicConfigBuilder(
        hk_version_obj=hk_version_obj, analysis_obj=balsamic_analysis_obj, lims_api=lims_api
    )

    # THEN assert that the correct case tags was used
    assert isinstance(file_handler.case_tags, CaseTags)


def test_include_delivery_report(mip_config_builder: MipConfigBuilder):
    # GIVEN a config builder with some data

    # GIVEN a config without a delivery report
    assert mip_config_builder.load_config.delivery_report is None

    # WHEN including the delivery report
    mip_config_builder.include_delivery_report()

    # THEN assert that the delivery report was added
    assert mip_config_builder.load_config.delivery_report is not None


def test_include_alignment_file_individual(mip_config_builder: MipConfigBuilder, sample_id: str):
    # GIVEN a mip config builder with some information

    # WHEN building the scout load config
    mip_config_builder.build_load_config()

    # THEN assert that the alignment file was added to sample id
    file_found = False
    for sample in mip_config_builder.load_config.samples:
        if sample.sample_id == sample_id:
            assert sample.alignment_path is not None
            file_found = True
    assert file_found


def test_include_mip_case_files(mip_config_builder: MipConfigBuilder):
    # GIVEN a housekeeper version bundle with some mip analysis files
    # GIVEN a case load object
    # GIVEN a mip file handler

    # WHEN including the case level files
    mip_config_builder.build_load_config()

    # THEN assert that the mandatory snv vcf was added
    assert mip_config_builder.load_config.vcf_snv


def test_include_mip_sample_files(mip_config_builder: MipConfigBuilder, sample_id: str):
    # GIVEN a housekeeper version bundle with some mip analysis files
    # GIVEN a case load object
    # GIVEN that there are no sample level mt_bam

    # GIVEN a mip file handler

    # WHEN including the case level files
    mip_config_builder.build_load_config()

    # THEN assert that the mandatory snv vcf was added
    file_found = False
    for sample in mip_config_builder.load_config.samples:
        if sample.sample_id == sample_id:
            assert sample.mt_bam is not None
            file_found = True
    assert file_found


def test_include_balsamic_case_files(balsamic_config_builder: BalsamicConfigBuilder):
    # GIVEN a housekeeper version bundle with some balsamic analysis files
    # GIVEN a case load object

    # WHEN including the case level files
    balsamic_config_builder.build_load_config()

    # THEN assert that the mandatory snv vcf was added
    assert balsamic_config_builder.load_config.vcf_cancer


def test_extract_generic_filepath(mip_config_builder: MipConfigBuilder):
    """Test that parsing of file path"""

    # GIVEN files paths ending with
    file_path1 = "/some/path/gatkcomb_rhocall_vt_af_chromograph_sites_X.png"
    file_path2 = "/some/path/gatkcomb_rhocall_vt_af_chromograph_sites_12.png"

    # THEN calling extracting the generic path will remove numeric id and fuffix
    generic_path = "/some/path/gatkcomb_rhocall_vt_af_chromograph_sites_"

    # THEN
    assert mip_config_builder.extract_generic_filepath(file_path1) == generic_path
    assert mip_config_builder.extract_generic_filepath(file_path2) == generic_path
