"""Fixtures for cli analysis tests"""
from datetime import datetime
from pathlib import Path

import pytest
from cg.constants import Pipeline, DataDelivery
from cg.models.cg_config import CGConfig
from cg.store import Store
from cg.store.models import Family
from tests.store_helpers import StoreHelpers


@pytest.fixture
def base_context(cg_context: CGConfig, analysis_store: Store) -> CGConfig:
    """context to use in cli"""
    cg_context.status_db_ = analysis_store
    return cg_context


@pytest.fixture(name="workflow_case_id")
def fixture_workflow_case_id() -> str:
    """Return a special case id"""
    return "dna_case"


@pytest.fixture(name="dna_sample_id")
def fixture_dna_sample_id() -> str:
    """Return a special sample id"""
    return "dna_sample"


@pytest.fixture(name="rna_sample_id")
def fixture_rna_sample_id() -> str:
    """Return a special sample id"""
    return "rna_sample"


@pytest.fixture(scope="function", name="analysis_store")
def fixture_analysis_store(
    base_store: Store, workflow_case_id: str, helpers: StoreHelpers
) -> Store:
    """Store to be used in tests"""
    _store = base_store

    case = helpers.add_case(_store, workflow_case_id, data_analysis=Pipeline.MIP_DNA)

    dna_sample = helpers.add_sample(
        _store, "dna_sample", is_rna=False, sequenced_at=datetime.now(), reads=10000000
    )
    helpers.add_relationship(_store, sample=dna_sample, case=case)

    case = helpers.add_case(_store, "rna_case", data_analysis=Pipeline.MIP_RNA)
    rna_sample = helpers.add_sample(
        _store, "rna_sample", is_rna=True, sequenced_at=datetime.now(), reads=10000000
    )
    helpers.add_relationship(_store, sample=rna_sample, case=case)

    case = helpers.add_case(_store, "dna_rna_mix_case", data_analysis=Pipeline.MIP_DNA)
    helpers.add_relationship(_store, sample=rna_sample, case=case)
    helpers.add_relationship(_store, sample=dna_sample, case=case)

    return _store


@pytest.fixture(name="fastq_context")
def fixture_fastq_context(
    base_context,
    cg_context: CGConfig,
    fastq_case,
    helpers: StoreHelpers,
    case_id,
) -> CGConfig:
    """Returns a CGConfig where the meta_apis["analysis_api"] is a FastqAnalysisAPI and a store
    containing a fastq case"""
    _store = cg_context.status_db
    # Add fastq case to db
    fastq_case["samples"][0]["sequenced_at"] = datetime.now()
    helpers.ensure_case_from_dict(store=_store, case_info=fastq_case)
    return cg_context


@pytest.fixture(name="fastq_case")
def fixture_fastq_case(case_id, family_name, sample_id, cust_sample_id, ticket_id: str) -> dict:
    """Returns a dict describing a fastq case"""
    return {
        "name": family_name,
        "panels": None,
        "internal_id": case_id,
        "data_analysis": Pipeline.FASTQ,
        "data_delivery": DataDelivery.FASTQ,
        "completed_at": None,
        "action": None,
        "tickets": ticket_id,
        "samples": [
            {
                "internal_id": sample_id,
                "sex": "male",
                "name": cust_sample_id,
                "original_ticket": ticket_id,
                "reads": 1000000,
                "capture_kit": "anything",
            },
        ],
    }


@pytest.fixture(scope="function")
def dna_case(analysis_store, helpers) -> Family:
    """Case with DNA application"""
    cust = helpers.ensure_customer(analysis_store)
    return analysis_store.get_case_by_name_and_customer(customer=cust, case_name="dna_case")


@pytest.fixture(scope="function")
def rna_case(analysis_store, helpers) -> Family:
    """Case with RNA application"""
    cust = helpers.ensure_customer(analysis_store)
    return analysis_store.get_case_by_name_and_customer(customer=cust, case_name="rna_case")


@pytest.fixture(scope="function")
def dna_rna_mix_case(analysis_store, helpers) -> Family:
    """Case with MIP analysis type DNA and RNA application"""
    cust = helpers.ensure_customer(analysis_store)
    return analysis_store.get_case_by_name_and_customer(customer=cust, case_name="dna_rna_mix_case")


@pytest.fixture(name="create_multiqc_html_file")
def fixture_create_multiqc_html_file(tmpdir_factory) -> Path:
    output_dir = tmpdir_factory.mktemp("output")
    file_path = Path(output_dir, "multiqc_report.html")
    file_path.touch(exist_ok=True)
    return file_path


@pytest.fixture(name="create_multiqc_json_file")
def fixture_create_multiqc_json_file(tmpdir_factory) -> Path:
    output_dir = tmpdir_factory.mktemp("output")
    file_path = Path(output_dir, "multiqc_report.json")
    file_path.touch(exist_ok=True)
    return file_path


class MockTB:
    """Trailblazer mock fixture"""

    def __init__(self):
        self._link_was_called = False
        self._mark_analyses_deleted_called = False
        self._add_pending_was_called = False
        self._add_pending_analysis_was_called = False
        self._family = None
        self._temp = None
        self._case_id = None
        self._email = None
        self._status = None

    def analyses(
        self,
        family=None,
        status=None,
        temp=None,
        case_id=None,
        query: str = None,
        deleted: bool = None,
        before=None,
        is_visible: bool = None,
    ):
        """Mock TB analyses models"""

        self._family = family
        self._status = status
        self._temp = temp

        if case_id == "yellowhog":
            return []

        class Row:
            """Mock a record representing an analysis"""

            def __init__(self):
                """We need to initialize _first_was_called
                so that we can set it in `first()` and retrieve
                it in `first_was_called()`. This way we can easily
                run the invoking code and make sure the function was
                called.
                """

                self._first_was_called = False

            def first(self):
                """Mock that the first row doesn't exist"""
                self._first_was_called = True

            def first_was_called(self):
                """Check if first was called"""
                return self._first_was_called

        return Row()

    def mark_analyses_deleted(self, case_id: str):
        """Mock this function"""
        self._case_id = case_id
        self._mark_analyses_deleted_called = True

    def add_pending(self, case_id: str, email: str):
        """Mock this function"""
        self._case_id = case_id
        self._email = email
        self._add_pending_was_called = True

    def add_pending_analysis(self, case_id: str, email: str):
        """Mock adding a pending analyses"""
        self._case_id = case_id
        self._email = email
        self._add_pending_analysis_was_called = True

    def mark_analyses_deleted_called(self):
        """check if mark_analyses_deleted was called"""
        return self._mark_analyses_deleted_called

    def add_pending_was_called(self):
        """check if add_pending was called"""
        return self._add_pending_was_called

    def is_latest_analysis_ongoing(self, case_id: str):
        """Override TrailblazerAPI is_ongoing method to avoid default behaviour"""
        return False

    def is_latest_analysis_failed(self, case_id: str):
        """Override TrailblazerAPI is_failed method to avoid default behaviour"""
        return False

    def is_latest_analysis_completed(self, case_id: str):
        """Override TrailblazerAPI is_completed method to avoid default behaviour"""
        return False

    def get_latest_analysis_status(self, case_id: str):
        """Override TrailblazerAPI get_analysis_status method to avoid default behaviour"""
        return None

    def has_latest_analysis_started(self, case_id: str):
        """Override TrailblazerAPI has_analysis_started method to avoid default behaviour"""
        return False

    def set_analysis_uploaded(self, case_id: str, uploaded_at: datetime):
        return None


@pytest.fixture(scope="function")
def tb_api():
    """Trailblazer API fixture"""

    return MockTB()
