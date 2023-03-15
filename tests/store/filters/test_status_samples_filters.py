from alchy import Query
from typing import List
from cg.constants.subject import PhenotypeStatus
from cg.constants.constants import SampleType
from cg.store import Store
from cg.store.models import Sample

from tests.store_helpers import StoreHelpers
from cg.store.filters.status_sample_filters import (
    filter_samples_with_loqusdb_id,
    filter_samples_without_loqusdb_id,
    filter_samples_is_delivered,
    filter_samples_is_not_delivered,
    filter_samples_without_invoice_id,
    filter_samples_is_down_sampled,
    filter_samples_is_not_down_sampled,
    filter_samples_is_sequenced,
    filter_samples_is_not_sequenced,
    filter_samples_do_invoice,
    filter_samples_do_not_invoice,
    filter_samples_by_invoice_id,
    filter_samples_by_internal_id,
    filter_samples_by_entry_id,
    filter_samples_with_type,
    filter_samples_is_prepared,
    filter_samples_is_not_prepared,
    filter_samples_is_received,
    filter_samples_is_not_received,
    filter_samples_by_name,
    filter_samples_by_subject_id,
)
from datetime import datetime
from tests.store.conftest import StoreConftestFixture


def test_get_samples_with_loqusdb_id(helpers, store, sample_store, sample_id, loqusdb_id):
    """Test sample extraction with Loqusdb ID."""

    # GIVEN a sample observations that has been uploaded to Loqusdb
    case = helpers.add_case(store)
    sample = helpers.add_sample(store, loqusdb_id=loqusdb_id)
    sample_not_uploaded = helpers.add_sample(store, internal_id=sample_id)
    sample_store.relate_sample(family=case, sample=sample, status=PhenotypeStatus.UNKNOWN)
    sample_store.relate_sample(
        family=case, sample=sample_not_uploaded, status=PhenotypeStatus.UNKNOWN
    )

    # GIVEN a sample query
    samples: Query = store._get_query(table=Sample)

    # WHEN retrieving the Loqusdb uploaded samples
    uploaded_samples = filter_samples_with_loqusdb_id(samples=samples)

    # THEN the obtained sample should match the expected one
    assert sample in uploaded_samples
    assert sample_not_uploaded not in uploaded_samples


def test_get_samples_without_loqusdb_id(helpers, store, sample_store, sample_id, loqusdb_id):
    """Test sample extraction without Loqusdb ID."""

    # GIVEN a sample observations that has not been uploaded to Loqusdb
    case = helpers.add_case(store)
    sample = helpers.add_sample(store)
    sample_uploaded = helpers.add_sample(store, internal_id=sample_id, loqusdb_id=loqusdb_id)
    sample_store.relate_sample(family=case, sample=sample, status=PhenotypeStatus.UNKNOWN)
    sample_store.relate_sample(family=case, sample=sample_uploaded, status=PhenotypeStatus.UNKNOWN)

    # GIVEN a sample query
    samples: Query = store._get_query(table=Sample)

    # WHEN retrieving the Loqusdb not uploaded samples
    not_uploaded_samples = filter_samples_without_loqusdb_id(samples=samples)

    # THEN the obtained sample should match the expected one
    assert sample in not_uploaded_samples
    assert sample_uploaded not in not_uploaded_samples


def test_filter_samples_is_delivered(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a delivered sample."""

    # GIVEN a store with two samples of which one is delivered

    # WHEN getting delivered samples
    samples: Query = filter_samples_is_delivered(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_not_delivered(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITHOUT_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is not delivered."""

    # GIVEN a store with two samples of which one is not delivered

    # WHEN getting not sequenced samples
    samples: Query = filter_samples_is_not_delivered(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_sample_query()
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_get_samples_by_invoice_id(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
    invoice_id=StoreConftestFixture.INVOICE_ID_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that has an invoice id."""

    # GIVEN a store with two samples of which oone has an invoice id

    # WHEN getting not sequenced samples
    samples: Query = filter_samples_by_invoice_id(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        ),
        invoice_id=invoice_id,
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_without_invoice_id(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITHOUT_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that has no invoice id."""

    # GIVEN a store with two samples of which one does not have an invoice id

    # WHEN getting not sequenced samples
    samples: Query = filter_samples_without_invoice_id(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_down_sampled(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is not down sampled."""

    # GIVEN a store with two samples of which one is not sequenced

    # WHEN getting not sequenced samples
    samples: Query = filter_samples_is_down_sampled(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_not_down_sampled(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITHOUT_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is not down sampled."""

    # GIVEN a store with two samples of which one is not sequenced

    # WHEN getting not sequenced samples
    samples: Query = filter_samples_is_not_down_sampled(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_sequenced(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is not sequenced."""

    # GIVEN a store with two samples of which one is not sequenced

    # WHEN getting not sequenced samples
    samples: Query = filter_samples_is_sequenced(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_not_sequenced(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITHOUT_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is not sequenced."""

    # GIVEN a store with two samples of which one is not sequenced

    # WHEN getting not sequenced samples
    samples: Query = filter_samples_is_not_sequenced(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_do_invoice(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is not a sample that should be invoiced."""

    # GIVEN a  store with two samples of which one is marked to skip invoicing

    # WHEN getting  samples mark to be invoiced
    samples: Query = filter_samples_do_invoice(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_do_not_invoice(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITHOUT_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is not a sample that should be invoiced."""

    # GIVEN a  store with two samples of which one is marked to skip invoicing

    # WHEN getting samples that are marked to skip invoicing
    samples: Query = filter_samples_do_not_invoice(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_delivered(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is delivered."""

    # GIVEN a store with two samples of which one is delivered

    # WHEN getting delivered samples
    samples: Query = filter_samples_is_delivered(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_not_delivered(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITHOUT_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is not delivered."""

    # GIVEN a store with two samples of which one is not delivered

    # WHEN getting not delivered samples
    samples: Query = filter_samples_is_not_delivered(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_received(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is received."""

    # GIVEN a store with two samples of which one is received

    # WHEN getting received samples
    samples: Query = filter_samples_is_received(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_not_received(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITHOUT_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is not received."""

    # GIVEN a store that has two samples of which one is not received

    # WHEN getting not received samples
    samples: Query = filter_samples_is_not_received(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_prepared(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is prepared."""

    # GIVEN a store that has two samples of which one is prepared

    samples: Query = filter_samples_is_prepared(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_samples_is_not_prepared(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name: str = StoreConftestFixture.NAME_SAMPLE_WITHOUT_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample that is not prepared."""

    # GIVEN a store that has two samples of which one is not prepared

    # WHEN getting not prepared samples
    samples: Query = filter_samples_is_not_prepared(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        )
    )

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].name == name


def test_filter_get_samples_by_internal_id(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    sample_id: str = StoreConftestFixture.INTERNAL_ID_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample with the given id."""

    # GIVEN a store with two samples of which one has the given internal id

    # WHEN getting a sample by id
    samples: Query = filter_samples_by_internal_id(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        ),
        internal_id=sample_id,
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.all()[0].internal_id == sample_id


def test_filter_get_samples_by_entry_id(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    entry_id: int = 1,
):
    """Test that a sample is returned when there is a sample with the given entry id."""

    # GIVEN a store with two samples

    # WHEN getting a sample by id
    samples: Query = filter_samples_by_entry_id(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        ),
        entry_id=entry_id,
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1


def test_filter_get_samples_with_type(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name=StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
    tissue_type: SampleType = SampleType.TUMOR,
):
    """Test that a sample is returned when there is a sample with the given type."""

    # GIVEN a store with two samples of which one is of the given type

    # WHEN getting a sample by type
    samples: Query = filter_samples_with_type(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        ),
        tissue_type=tissue_type,
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.first().name == name


def test_filter_get_samples_by_name(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    name=StoreConftestFixture.NAME_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample with the given type."""
    # GIVEN a store with two samples that have names

    # WHEN getting a sample by name
    samples: Query = filter_samples_by_name(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        ),
        name=name,
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.first().name == name


def test_filter_get_samples_by_subject_id(
    store_with_a_sample_that_has_many_attributes_and_one_without: Store,
    subject_id: str = StoreConftestFixture.SUBJECT_ID_SAMPLE_WITH_ATTRIBUTES.value,
):
    """Test that a sample is returned when there is a sample with the given subject id."""
    # GIVEN a store with two samples of which one has a subject id

    # WHEN getting a sample by subject id
    samples: Query = filter_samples_by_subject_id(
        samples=store_with_a_sample_that_has_many_attributes_and_one_without._get_query(
            table=Sample
        ),
        subject_id=subject_id,
    )

    # ASSERT that samples is a query
    assert isinstance(samples, Query)

    # THEN samples should contain the test sample
    assert samples.all() and len(samples.all()) == 1 and samples.first().subject_id == subject_id
