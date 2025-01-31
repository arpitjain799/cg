"""Fixtures for the meta tests."""
import datetime as dt
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest

from cg.apps.cgstats.db.models import (
    Datasource,
    Flowcell,
    Project,
    Sample,
    Supportparams,
    Unaligned,
)
from cg.apps.cgstats.stats import StatsAPI
from cg.apps.housekeeper.hk import HousekeeperAPI

from cg.constants.housekeeper_tags import HkMipAnalysisTag
from cg.constants.sequencing import Sequencers
from cg.meta.transfer import TransferFlowCell
from cg.meta.workflow.mip_dna import MipDNAAnalysisAPI
from cg.store import Store
from cg.store.models import Customer, ApplicationVersion, Invoice, Sample
from tests.mocks.hk_mock import MockHousekeeperAPI
from tests.store_helpers import StoreHelpers
from tests.mocks.limsmock import MockLimsAPI
from cg.constants.sequencing import RecordType
from cg.constants.invoice import CustomerNames
from cg.meta.invoice import InvoiceAPI


@pytest.fixture(scope="function", name="mip_hk_store")
def fixture_mip_hk_store(
    helpers: StoreHelpers,
    real_housekeeper_api: HousekeeperAPI,
    timestamp: datetime,
    case_id: str,
) -> HousekeeperAPI:
    deliver_hk_bundle_data = {
        "name": case_id,
        "created": timestamp,
        "expires": timestamp,
        "files": [
            {
                "path": "tests/fixtures/apps/mip/dna/store/case_config.yaml",
                "archive": False,
                "tags": ["mip-config"],
            },
            {
                "path": "tests/fixtures/apps/mip/dna/store/case_qc_sample_info.yaml",
                "archive": False,
                "tags": ["sampleinfo"],
            },
            {
                "path": "tests/fixtures/apps/mip/case_metrics_deliverables.yaml",
                "archive": False,
                "tags": HkMipAnalysisTag.QC_METRICS,
            },
            {
                "path": "tests/fixtures/apps/mip/case_file.txt",
                "archive": False,
                "tags": ["case-tag"],
            },
            {
                "path": "tests/fixtures/apps/mip/sample_file.txt",
                "archive": False,
                "tags": ["sample-tag", "ADM1"],
            },
        ],
    }
    helpers.ensure_hk_bundle(real_housekeeper_api, deliver_hk_bundle_data, include=True)

    empty_deliver_hk_bundle_data = {
        "name": "case_missing_data",
        "created": timestamp,
        "expires": timestamp,
        "files": [
            {
                "path": "tests/fixtures/apps/mip/dna/store/empty_case_config.yaml",
                "archive": False,
                "tags": ["mip-config"],
            },
            {
                "path": "tests/fixtures/apps/mip/dna/store/empty_case_qc_sample_info.yaml",
                "archive": False,
                "tags": ["sampleinfo"],
            },
            {
                "path": "tests/fixtures/apps/mip/dna/store/empty_case_metrics_deliverables.yaml",
                "archive": False,
                "tags": HkMipAnalysisTag.QC_METRICS,
            },
            {
                "path": "tests/fixtures/apps/mip/case_file.txt",
                "archive": False,
                "tags": ["case-tag"],
            },
            {
                "path": "tests/fixtures/apps/mip/sample_file.txt",
                "archive": False,
                "tags": ["sample-tag", "ADM1"],
            },
        ],
    }
    helpers.ensure_hk_bundle(real_housekeeper_api, empty_deliver_hk_bundle_data, include=True)

    return real_housekeeper_api


@pytest.fixture()
def mip_analysis_api(context_config, mip_hk_store, analysis_store):
    """Return a MIP analysis API."""
    analysis_api = MipDNAAnalysisAPI(context_config)
    analysis_api.housekeeper_api = mip_hk_store
    analysis_api.status_db = analysis_store
    return analysis_api


@pytest.fixture(name="binary_path")
def fixture_binary_path() -> str:
    """Return the string of a path to a (fake) binary."""
    return Path("usr", "bin", "binary").as_posix()


@pytest.fixture(name="yet_another_flow_cell_id")
def fixture_yet_another_flow_cell_id() -> str:
    """Return flow cell id."""
    return "HJKMYBCXX"


@pytest.fixture(name="stats_sample_data")
def fixture_stats_sample_data(
    sample_id: str, flow_cell_id: str, yet_another_flow_cell_id: str
) -> dict:
    return {
        "samples": [
            {
                "name": sample_id,
                "index": "ACGTACAT",
                "flowcell": flow_cell_id,
                "type": Sequencers.HISEQX,
            },
            {
                "name": "ADM1136A3",
                "index": "ACGTACAT",
                "flowcell": yet_another_flow_cell_id,
                "type": Sequencers.HISEQX,
            },
        ]
    }


@pytest.fixture(name="store_stats")
def fixture_store_stats() -> Generator[StatsAPI, None, None]:
    """Setup base CGStats store."""
    _store: StatsAPI = StatsAPI(
        {
            "cgstats": {
                "binary_path": "echo",
                "database": "sqlite://",
                "root": "tests/fixtures/DEMUX",
            }
        }
    )
    _store.create_all()
    yield _store
    _store.drop_all()


@pytest.fixture(name="base_store_stats")
def fixture_base_store_stats(
    store_stats: StatsAPI, stats_sample_data: dict
) -> Generator[StatsAPI, None, None]:
    """Setup CGStats store with sample data."""
    demuxes: dict = {}
    for sample_data in stats_sample_data["samples"]:
        project: Project = store_stats.Project(projectname="test", time=dt.datetime.now())
        sample: Sample = store_stats.Sample(
            samplename=sample_data["name"],
            barcode=sample_data["index"],
            limsid=sample_data["name"],
        )
        sample.project = project
        unaligned: Unaligned = store_stats.Unaligned(readcounts=300000000, q30_bases_pct=85)
        unaligned.sample = sample

        if sample_data["flowcell"] in demuxes:
            demux = demuxes[sample_data["flowcell"]]
        else:
            flowcell: Flowcell = store_stats.Flowcell(
                flowcellname=sample_data["flowcell"],
                flowcell_pos="A",
                hiseqtype=sample_data["type"],
                time=dt.datetime.now(),
            )
            supportparams: Supportparams = store_stats.Supportparams(
                document_path="NA" + sample_data["name"], idstring="NA"
            )
            datasource: Datasource = store_stats.Datasource(
                document_path="NA" + sample_data["name"], document_type="html"
            )
            datasource.supportparams = supportparams
            demux = store_stats.Demux()
            demux.flowcell = flowcell
            demux.datasource = datasource
            demuxes[sample_data["flowcell"]] = demux

        unaligned.demux = demux
        store_stats.add(unaligned)
    store_stats.commit()
    yield store_stats


@pytest.fixture(name="flowcell_store")
def fixture_flowcell_store(
    base_store: Store, stats_sample_data: dict
) -> Generator[Store, None, None]:
    """Setup store with sample data for testing flow cell transfer."""
    for sample_data in stats_sample_data["samples"]:
        customer: Customer = (base_store.get_customers())[0]
        application_version: ApplicationVersion = base_store.get_application_by_tag(
            "WGSPCFC030"
        ).versions[0]
        sample: Sample = base_store.add_sample(
            name="NA", sex="male", internal_id=sample_data["name"]
        )
        sample.customer = customer
        sample.application_version = application_version
        sample.received_at = dt.datetime.now()
        base_store.session.add(sample)
    base_store.session.commit()
    yield base_store


@pytest.fixture(name="transfer_flow_cell_api")
def fixture_transfer_flow_cell_api(
    flowcell_store: Store, housekeeper_api: MockHousekeeperAPI, base_store_stats: StatsAPI
) -> Generator[TransferFlowCell, None, None]:
    """Setup transfer flow cell API."""
    yield TransferFlowCell(db=flowcell_store, stats_api=base_store_stats, hk_api=housekeeper_api)


@pytest.fixture(name="get_invoice_api_sample")
def fixture_invoice_api_sample(
    store: Store,
    lims_api: MockLimsAPI,
    helpers: StoreHelpers,
    invoice_id: int = 0,
    customer_id: str = CustomerNames.cust132,
) -> InvoiceAPI:
    """Return an InvoiceAPI with samples."""
    sample = helpers.add_sample(store, customer_id=customer_id)
    invoice: Invoice = helpers.ensure_invoice(
        store,
        invoice_id=invoice_id,
        customer_id=customer_id,
        samples=[sample],
    )
    return InvoiceAPI(store, lims_api, invoice)


@pytest.fixture(name="get_invoice_api_nipt_customer")
def fixture_invoice_api_nipt_customer(
    store: Store,
    lims_api: MockLimsAPI,
    helpers: StoreHelpers,
    invoice_id: int = 0,
    customer_id: str = CustomerNames.cust032,
) -> InvoiceAPI:
    """Return an InvoiceAPI with a pool for NIPT customer."""
    pool = helpers.ensure_pool(store=store, customer_id=customer_id)
    invoice: Invoice = helpers.ensure_invoice(
        store,
        invoice_id=invoice_id,
        customer_id=customer_id,
        pools=[pool],
    )
    return InvoiceAPI(store, lims_api, invoice)


@pytest.fixture(name="get_invoice_api_pool_generic_customer")
def fixture_invoice_api_pool_generic_customer(
    store: Store,
    lims_api: MockLimsAPI,
    helpers: StoreHelpers,
    invoice_id: int = 0,
    record_type: str = RecordType.Pool,
    customer_id: str = CustomerNames.cust132,
) -> InvoiceAPI:
    """Return an InvoiceAPI with a pool."""
    pool = helpers.ensure_pool(store=store, customer_id=customer_id)
    invoice: Invoice = helpers.ensure_invoice(
        store,
        invoice_id=invoice_id,
        pools=[pool],
        customer_id=customer_id,
    )
    return InvoiceAPI(store, lims_api, invoice)
