"""Tests for the file handlers."""
import logging
from pathlib import Path

from cg.constants.constants import SampleType
from cg.models.scout.scout_load_config import ScoutCancerIndividual

from housekeeper.store.models import Version

from cg.meta.upload.scout.balsamic_config_builder import BalsamicConfigBuilder
from cg.meta.upload.scout.hk_tags import CaseTags
from cg.meta.upload.scout.mip_config_builder import MipConfigBuilder
from cg.meta.upload.scout.rnafusion_config_builder import RnafusionConfigBuilder
from cg.store.models import Analysis
from tests.mocks.limsmock import MockLimsAPI
from tests.mocks.madeline import MockMadelineAPI
from tests.mocks.mip_analysis_mock import MockMipAnalysis

from tests.apps.scout.conftest import fixture_scout_individual


def test_mip_config_builder(
    hk_version: Version,
    mip_dna_analysis: Analysis,
    lims_api: MockLimsAPI,
    mip_analysis_api: MockMipAnalysis,
    madeline_api: MockMadelineAPI,
):
    """Test MIP config builder class."""
    # GIVEN a MIP analysis

    # WHEN instantiating
    config_builder = MipConfigBuilder(
        hk_version_obj=hk_version,
        analysis_obj=mip_dna_analysis,
        lims_api=lims_api,
        mip_analysis_api=mip_analysis_api,
        madeline_api=madeline_api,
    )

    # THEN assert that the correct case tags was used
    assert isinstance(config_builder.case_tags, CaseTags)


def test_balsamic_config_builder(
    hk_version: Version, balsamic_analysis_obj: Analysis, lims_api: MockLimsAPI
):
    """Test Balsamic config builder class."""
    # GIVEN a balsamic file handler

    # WHEN instantiating
    file_handler = BalsamicConfigBuilder(
        hk_version_obj=hk_version, analysis_obj=balsamic_analysis_obj, lims_api=lims_api
    )

    # THEN assert that the correct case tags was used
    assert isinstance(file_handler.case_tags, CaseTags)


def test_rnafusion_config_builder(
    hk_version: Version,
    rnafusion_analysis_obj: Analysis,
    lims_api: MockLimsAPI,
):
    """Test RNAfusion config builder class."""
    # GIVEN a rnafusion file handler

    # WHEN instantiating
    file_handler = RnafusionConfigBuilder(
        hk_version_obj=hk_version, analysis_obj=rnafusion_analysis_obj, lims_api=lims_api
    )

    # THEN assert that the correct case tags was used
    assert isinstance(file_handler.case_tags, CaseTags)


def test_include_delivery_report_mip(mip_config_builder: MipConfigBuilder):
    """Test include delivery report."""
    # GIVEN a config builder with data

    # GIVEN a config without a delivery report
    assert mip_config_builder.load_config.delivery_report is None

    # WHEN including the delivery report
    mip_config_builder.include_delivery_report()

    # THEN assert that the delivery report was added
    assert mip_config_builder.load_config.delivery_report is not None


def test_include_synopsis(mip_config_builder: MipConfigBuilder):
    """Test include synopsis."""
    # GIVEN a config builder with some data

    # GIVEN a config without synopsis
    assert mip_config_builder.load_config.synopsis is None

    # WHEN including the synopsis
    mip_config_builder.build_load_config()

    # THEN assert that the synopsis was added
    assert mip_config_builder.load_config.synopsis


def test_include_phenotype_groups(mip_config_builder: MipConfigBuilder):
    """Test include phenotype groups."""
    # GIVEN a config builder with some data

    # GIVEN a config without a phenotype groups
    assert mip_config_builder.load_config.phenotype_groups is None

    # WHEN including the phenotype groups
    mip_config_builder.include_phenotype_groups()

    # THEN assert that the phenotype groups were added
    assert mip_config_builder.load_config.phenotype_groups is not None


def test_include_phenotype_terms(mip_config_builder: MipConfigBuilder):
    """Test include phenotype terms."""
    # GIVEN a config builder with some data

    # GIVEN a config without a phenotype terms
    assert mip_config_builder.load_config.phenotype_terms is None

    # WHEN including the phenotype terms
    mip_config_builder.include_phenotype_terms()

    # THEN assert that the phenotype terms were added
    assert mip_config_builder.load_config.phenotype_terms is not None


def test_include_alignment_file_individual(mip_config_builder: MipConfigBuilder, sample_id: str):
    """Test include alignment files."""
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
    """Test include MIP case files."""
    # GIVEN a Housekeeper version bundle with MIP analysis files
    # GIVEN a case load object
    # GIVEN a MIP file handler

    # WHEN including the case level files
    mip_config_builder.build_load_config()

    # THEN assert that the mandatory SNV VCF was added
    assert mip_config_builder.load_config.vcf_snv


def test_include_mip_sample_files(mip_config_builder: MipConfigBuilder, sample_id: str):
    """Test include MIP sample files."""
    # GIVEN a Housekeeper version bundle with MIP analysis files
    # GIVEN a case load object
    # GIVEN that there are no sample level mt_bam

    # GIVEN a MIP file handler

    # WHEN including the case level files
    mip_config_builder.build_load_config()

    # THEN assert that the mandatory SNV VCF was added
    file_found = False
    for sample in mip_config_builder.load_config.samples:
        if sample.sample_id == sample_id:
            assert sample.mt_bam is not None
            file_found = True
    assert file_found


def test_include_mip_sample_subject_id(
    mip_config_builder: MipConfigBuilder, sample_id: str, caplog
):
    """Test include MIP sample subject id."""
    # GIVEN subject_id on the sample
    caplog.set_level(level=logging.DEBUG)

    # WHEN building the config
    mip_config_builder.build_load_config()

    # THEN the subject_id was added to the scout sample
    subject_id_found = False
    for sample in mip_config_builder.load_config.samples:
        if sample.sample_id == sample_id:
            subject_id_found = True
            assert sample.subject_id is not None
    assert subject_id_found


def test_include_balsamic_case_files(balsamic_config_builder: BalsamicConfigBuilder):
    """Test include Balsamic case files."""
    # GIVEN a Housekeeper version bundle with balsamic analysis files
    # GIVEN a case load object

    # WHEN including the case level files
    balsamic_config_builder.build_load_config()

    # THEN assert that the mandatory snv vcf was added
    assert balsamic_config_builder.load_config.vcf_cancer


def test_include_balsamic_delivery_report(balsamic_config_builder: BalsamicConfigBuilder):
    """Test include Balsamic delivery report."""
    # GIVEN a Housekeeper version bundle with balsamic analysis files
    # GIVEN a case load object

    # WHEN including the case level files
    balsamic_config_builder.build_load_config()

    # THEN assert that the delivery_report exists
    assert balsamic_config_builder.load_config.delivery_report


def test_extract_generic_filepath(mip_config_builder: MipConfigBuilder):
    """Test that parsing of file path."""

    # GIVEN files paths ending with
    file_path1 = "/some/path/gatkcomb_rhocall_vt_af_chromograph_sites_X.png"
    file_path2 = "/some/path/gatkcomb_rhocall_vt_af_chromograph_sites_12.png"

    # THEN calling extracting the generic path will remove numeric id and fuffix
    generic_path = "/some/path/gatkcomb_rhocall_vt_af_chromograph_sites_"

    # THEN
    assert mip_config_builder.extract_generic_filepath(file_path1) == generic_path
    assert mip_config_builder.extract_generic_filepath(file_path2) == generic_path


def test_get_sample_id(
    sample_id: str, scout_individual: dict, balsamic_config_builder: BalsamicConfigBuilder
):
    """Test get sample id given a Scout individual when no alignment path is provided."""

    # GIVEN a scout individual
    config_sample: ScoutCancerIndividual = ScoutCancerIndividual(**scout_individual)
    config_sample.alignment_path = None

    # WHEN getting the sample ID
    balsamic_sample_id: str = balsamic_config_builder._get_sample_id(config_sample)

    # THEN the sample ID should match the expected one
    assert balsamic_sample_id == sample_id


def test_get_sample_id_no_alignment_path(
    scout_individual: dict, balsamic_config_builder: BalsamicConfigBuilder
):
    """Test get sample id given a Scout individual with a tumor alignment path."""

    # GIVEN a scout individual with a tumor sample alignment bam
    config_sample: ScoutCancerIndividual = ScoutCancerIndividual(**scout_individual)
    config_sample.alignment_path = Path("path", "to", "tumor_sample.bam").as_posix()

    # WHEN getting the sample ID
    balsamic_sample_id: str = balsamic_config_builder._get_sample_id(config_sample)

    # THEN the sample ID should be "tumor"
    assert balsamic_sample_id == SampleType.TUMOR.value
