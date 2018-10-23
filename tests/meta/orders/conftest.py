import json

import pytest

from cg.apps.osticket import OsTicket
from cg.meta.orders import OrdersAPI, OrderType
from cg.meta.orders.status import StatusHandler


class MockLims:

    def update_sample(self, lims_id: str, sex=None, application: str=None,
                      target_reads: int=None):
        pass


@pytest.fixture
def scout_order():
    """Load an example scout order."""
    json_path = 'tests/fixtures/orders/scout.json'
    json_data = json.load(open(json_path))
    return json_data


@pytest.fixture
def external_order():
    """Load an example external order."""
    json_path = 'tests/fixtures/orders/external.json'
    json_data = json.load(open(json_path))
    return json_data


@pytest.fixture
def fastq_order():
    """Load an example fastq order."""
    json_path = 'tests/fixtures/orders/fastq.json'
    json_data = json.load(open(json_path))
    return json_data


@pytest.fixture
def rml_order():
    """Load an example rml order."""
    json_path = 'tests/fixtures/orders/rml.json'
    json_data = json.load(open(json_path))
    return json_data


@pytest.fixture
def metagenome_order():
    """Load an example metagenome order."""
    json_path = 'tests/fixtures/orders/metagenome.json'
    json_data = json.load(open(json_path))
    return json_data

@pytest.fixture    
def microbial_order():
    """Load an example microbial order."""
    json_path = 'tests/fixtures/orders/microbial.json'
    json_data = json.load(open(json_path))
    return json_data


@pytest.fixture
def all_orders(rml_order, fastq_order, scout_order, external_order, microbial_order, metagenome_order):
    return {
        OrderType.RML: rml_order,
        OrderType.FASTQ: fastq_order,
        OrderType.SCOUT: scout_order,
        OrderType.EXTERNAL: external_order,
        OrderType.MICROBIAL: microbial_order,
        OrderType.METAGENOME: metagenome_order,        
    }


@pytest.fixture
def rml_status_data(rml_order):
    """Parse rml order example."""
    data = StatusHandler.pools_to_status(rml_order)
    return data


@pytest.fixture
def fastq_status_data(fastq_order):
    """Parse fastq order example."""
    data = StatusHandler.samples_to_status(fastq_order)
    return data


@pytest.fixture
def scout_status_data(scout_order):
    """Parse scout order example."""
    data = StatusHandler.families_to_status(scout_order)
    return data

@pytest.fixture
def external_status_data(external_order):
    """Parse external order example."""
    data = StatusHandler.families_to_status(external_order)
    return data

@pytest.fixture
def microbial_status_data(microbial_order):
    """Parse microbial order example."""
    data = StatusHandler.microbial_samples_to_status(microbial_order)
    return data


@pytest.fixture(scope='function')
def orders_api(base_store):
    osticket_api = OsTicket()
    lims = MockLims()
    _orders_api = OrdersAPI(lims=lims, status=base_store, osticket=osticket_api)
    return _orders_api
