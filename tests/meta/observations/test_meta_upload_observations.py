"""Test observations API methods."""

import logging
from typing import Dict

import pytest
from _pytest.logging import LogCaptureFixture

from cg.apps.loqus import LoqusdbAPI
from cg.constants.observations import LoqusdbInstance
from cg.constants.sequencing import SequencingMethod
from cg.exc import LoqusdbDuplicateRecordError, LoqusdbUploadCaseError, CaseNotFoundError
from cg.meta.observations.mip_dna_observations_api import MipDNAObservationsAPI
from cg.models.cg_config import CGConfig
from cg.models.observations.input_files import MipDNAObservationsInputFiles
from cg.store import models, Store
from tests.store_helpers import StoreHelpers


def test_observations_upload(
    case_id: str,
    mip_dna_observations_api: MipDNAObservationsAPI,
    observations_input_files: MipDNAObservationsInputFiles,
    nr_of_loaded_variants,
    analysis_store: Store,
    caplog: LogCaptureFixture,
    mocker,
):
    """Test upload observations method."""
    caplog.set_level(logging.DEBUG)

    # GIVEN a mocked observations API and a list of mocked observations files
    case: models.Family = analysis_store.family(case_id)
    mocker.patch.object(
        mip_dna_observations_api,
        "get_observations_input_files",
        return_value=observations_input_files,
    )
    mocker.patch.object(mip_dna_observations_api, "is_duplicate", return_value=False)

    # WHEN uploading the case observations to Loqusdb
    mip_dna_observations_api.upload(case)

    # THEN the case should be successfully uploaded
    assert f"Uploaded {nr_of_loaded_variants} variants to Loqusdb" in caplog.text


def test_get_loqusdb_api(
    mip_dna_observations_api: MipDNAObservationsAPI,
    loqusdb_config_dict: Dict[LoqusdbInstance, dict],
):
    """Test Loqusdb API retrieval given a Loqusdb instance."""

    # GIVEN the expected Loqusdb config dictionary

    # GIVEN a WES Loqusdb instance and an observations API
    loqusdb_instance = LoqusdbInstance.WES

    # WHEN calling the Loqusdb API get method
    loqusdb_api: LoqusdbAPI = mip_dna_observations_api.get_loqusdb_api(loqusdb_instance)

    # THEN a WES loqusdb api should be returned
    assert isinstance(loqusdb_api, LoqusdbAPI)
    assert loqusdb_api.binary_path == loqusdb_config_dict[LoqusdbInstance.WES]["binary_path"]
    assert loqusdb_api.config_path == loqusdb_config_dict[LoqusdbInstance.WES]["config_path"]


def test_mip_dna_get_loqusdb_instance(mip_dna_observations_api: MipDNAObservationsAPI):
    """Test Loqusdb instance retrieval given a sequencing method."""

    # GIVEN a rare disease observations API with a WES as sequencing method
    mip_dna_observations_api.sequencing_method = SequencingMethod.WES

    # WHEN getting the Loqusdb instance
    loqusdb_instance = mip_dna_observations_api.get_loqusdb_instance()

    # THEN the correct loqusdb instance should be returned
    assert loqusdb_instance == LoqusdbInstance.WES


def test_mip_dna_get_loqusdb_instance_not_supported(
    mip_dna_observations_api: MipDNAObservationsAPI, caplog: LogCaptureFixture
):
    """Test Loqusdb instance retrieval given a not supported sequencing method."""

    # GIVEN a rare disease observations API with a WTS sequencing method
    mip_dna_observations_api.sequencing_method = SequencingMethod.WTS

    # WHEN getting the Loqusdb instance
    with pytest.raises(LoqusdbUploadCaseError):
        # THEN the upload should be canceled
        mip_dna_observations_api.get_loqusdb_instance()

    assert (
        f"Sequencing method {SequencingMethod.WTS} is not supported by Loqusdb. Cancelling upload."
        in caplog.text
    )


def test_mip_dna_load_observations(
    case_id: str,
    mip_dna_observations_api: MipDNAObservationsAPI,
    observations_input_files: MipDNAObservationsInputFiles,
    nr_of_loaded_variants,
    analysis_store: Store,
    caplog: LogCaptureFixture,
    mocker,
):
    """Test loading of case observations for rare disease."""
    caplog.set_level(logging.DEBUG)

    # GIVEN a mock MIP DNA observations API  and a list of observations input files
    case: models.Family = analysis_store.family(case_id)
    mocker.patch.object(mip_dna_observations_api, "is_duplicate", return_value=False)

    # WHEN loading the case to Loqusdb
    mip_dna_observations_api.load_observations(case, observations_input_files)

    # THEN the observations should be loaded without any errors
    assert f"Uploaded {nr_of_loaded_variants} variants to Loqusdb" in caplog.text


def test_mip_dna_load_observations_duplicate(
    case_id: str,
    mip_dna_observations_api: MipDNAObservationsAPI,
    observations_input_files: MipDNAObservationsInputFiles,
    analysis_store: Store,
    caplog: LogCaptureFixture,
    mocker,
):
    """Test upload case duplicate to Loqusdb."""
    caplog.set_level(logging.DEBUG)

    # GIVEN a mocked observations API and a case object that has already been uploaded to Loqusdb
    case: models.Family = analysis_store.family(case_id)
    mocker.patch.object(mip_dna_observations_api, "is_duplicate", return_value=True)

    # WHEN uploading the case observations to Loqusdb
    with pytest.raises(LoqusdbDuplicateRecordError):
        # THEN a duplicate record error should be raised
        mip_dna_observations_api.load_observations(case, observations_input_files)

    assert f"Case {case.internal_id} has been already uploaded to Loqusdb" in caplog.text


def test_mip_dna_load_observations_tumor_case(
    case_id: str,
    mip_dna_observations_api: MipDNAObservationsAPI,
    observations_input_files: MipDNAObservationsInputFiles,
    analysis_store: Store,
    caplog: LogCaptureFixture,
    mocker,
):
    """Test loading of a tumor case to Loqusdb."""
    caplog.set_level(logging.DEBUG)

    # GIVEN a MIP DNA observations API and a case object with a tumour sample
    case: models.Family = analysis_store.family(case_id)
    mocker.patch.object(mip_dna_observations_api, "is_duplicate", return_value=False)
    case.links[0].sample.is_tumour = True

    # WHEN getting the Loqusdb API
    with pytest.raises(LoqusdbUploadCaseError):
        # THEN an upload error should be raised and the execution aborted
        mip_dna_observations_api.load_observations(case, observations_input_files)

    assert f"Case {case.internal_id} has tumour samples. Cancelling upload." in caplog.text


def test_mip_dna_is_duplicate(
    case_id: str,
    mip_dna_observations_api: MipDNAObservationsAPI,
    observations_input_files: MipDNAObservationsInputFiles,
    analysis_store: Store,
    mocker,
):
    """Test duplicate extraction for a case that is not Loqusdb."""

    # GIVEN a Loqusdb instance with no case duplicates
    case: models.Family = analysis_store.family(case_id)
    mocker.patch.object(mip_dna_observations_api.loqusdb_api, "get_case", return_value=None)
    mocker.patch.object(mip_dna_observations_api.loqusdb_api, "get_duplicate", return_value=False)

    # WHEN checking that a case has not been uploaded to Loqusdb
    is_duplicate: bool = mip_dna_observations_api.is_duplicate(
        case=case, profile_vcf_path=observations_input_files.profile_vcf_path
    )

    # THEN there should be no duplicates in Loqusdb
    assert is_duplicate is False


def test_mip_dna_is_duplicate_case_output(
    case_id: str,
    observations_input_files: MipDNAObservationsInputFiles,
    mip_dna_observations_api: MipDNAObservationsAPI,
    analysis_store: Store,
):
    """Test duplicate extraction for a case that already exists in Loqusdb."""

    # GIVEN a Loqusdb instance with a duplicated case
    case: models.Family = analysis_store.family(case_id)

    # WHEN checking that a case has been already uploaded to Loqusdb
    is_duplicate: bool = mip_dna_observations_api.is_duplicate(
        case=case, profile_vcf_path=observations_input_files.profile_vcf_path
    )

    # THEN an upload of a duplicate case should be detected
    assert is_duplicate is True


def test_mip_dna_is_duplicate_loqusdb_id(
    case_id: str,
    loqusdb_id: str,
    mip_dna_observations_api: MipDNAObservationsAPI,
    observations_input_files: MipDNAObservationsInputFiles,
    analysis_store: Store,
    mocker,
):
    """Test duplicate extraction for a case that already exists in Loqusdb."""

    # GIVEN a Loqusdb instance with a duplicated case and whose samples already have a Loqusdb ID
    case: models.Family = analysis_store.family(case_id)
    case.links[0].sample.loqusdb_id = loqusdb_id
    mocker.patch.object(mip_dna_observations_api.loqusdb_api, "get_case", return_value=None)
    mocker.patch.object(mip_dna_observations_api.loqusdb_api, "get_duplicate", return_value=False)

    # WHEN checking that the sample observations have already been uploaded
    is_duplicate: bool = mip_dna_observations_api.is_duplicate(
        case=case, profile_vcf_path=observations_input_files.profile_vcf_path
    )

    # THEN a duplicated upload should be identified
    assert is_duplicate is True


def test_mip_dna_delete_case(
    case_id: str,
    mip_dna_observations_api: MipDNAObservationsAPI,
    analysis_store: Store,
    caplog: LogCaptureFixture,
):
    """Test delete case from Loqusdb."""
    caplog.set_level(logging.DEBUG)

    # GIVEN a Loqusdb instance filled with a case
    case: models.Family = analysis_store.family(case_id)

    # WHEN deleting a case
    mip_dna_observations_api.delete_case(case)

    # THEN the case should be deleted from Loqusdb
    assert f"Removed observations for case {case.internal_id} from Loqusdb" in caplog.text


def test_mip_dna_delete_case_not_found(
    base_context: CGConfig,
    helpers: StoreHelpers,
    loqusdb_api: LoqusdbAPI,
    mip_dna_observations_api: MipDNAObservationsAPI,
    caplog: LogCaptureFixture,
):
    """Test delete case from Loqusdb that has not been uploaded."""
    store: Store = base_context.status_db

    # GIVEN an observations instance and a case that has not been uploaded to Loqusdb
    loqusdb_api.process.stdout = None
    mip_dna_observations_api.loqusdb_api = loqusdb_api
    case: models.Family = helpers.add_case(store)

    # WHEN deleting a rare disease case that does not exist in Loqusdb
    with pytest.raises(CaseNotFoundError):
        # THEN a CaseNotFoundError should be raised
        mip_dna_observations_api.delete_case(case)

    assert (
        f"Case {case.internal_id} could not be found in Loqusdb. Skipping case deletion."
        in caplog.text
    )