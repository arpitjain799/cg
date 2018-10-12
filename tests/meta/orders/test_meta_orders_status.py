import datetime as dt

import pytest
from cg.exc import OrderError
from cg.meta.orders.status import StatusHandler


def test_pools_to_status(rml_order):
    # GIVEN a rml order with three samples in one pool
    # WHEN parsing for status
    data = StatusHandler.pools_to_status(rml_order)
    # THEN it should pick out the general information
    assert data['customer'] == 'cust001'
    assert data['order'] == 'ctDNA sequencing - order 9'
    # ... and information about the pool(s)
    assert len(data['pools']) == 1
    assert data['pools'][0]['name'] == '1'
    assert data['pools'][0]['application'] == 'RMLS05R150'
    assert data['pools'][0]['capture_kit'] == 'Agilent Sureselect CRE'


def test_samples_to_status(fastq_order):
    # GIVEN fastq order with two samples
    # WHEN parsing for status
    data = StatusHandler.samples_to_status(fastq_order)
    # THEN it should pick out samples and relevant information
    assert len(data['samples']) == 2
    first_sample = data['samples'][0]
    assert first_sample['name'] == 'sample-normal'
    assert first_sample['application'] == 'WGSPCFC060'
    assert first_sample['priority'] == 'priority'
    assert first_sample['tumour'] is False

    # ... and the other sample is a tumour
    assert data['samples'][1]['tumour'] is True


def test_microbial_samples_to_status(microbial_order):
    # GIVEN microbial order with three samples

    # WHEN parsing for status
    data = StatusHandler.microbial_samples_to_status(microbial_order)

    # THEN it should pick out samples and relevant information
    assert len(data['samples']) == 5
    assert data['customer'] == 'cust002'
    assert data['order'] == 'Microbial samples'
    assert data['comment'] == 'Order comment'

    # THEN first sample should contain all the relevant data from the microbial order
    sample_data = data['samples'][0]
    assert sample_data.get('priority') in 'research'
    assert sample_data['name'] == 'all-fields'
    assert sample_data.get('internal_id') is None
    assert sample_data['strain'] == 'Other'
    assert sample_data['strain_other'] == 'M.upium'
    assert sample_data['reference_genome'] == 'NC_111'
    assert sample_data['application'] == 'MWRNXTR003'
    assert sample_data['comment'] == 'plate comment'


def test_families_to_status(scout_order):
    # GIVEN a scout order with a trio family
    # WHEN parsing for status
    data = StatusHandler.families_to_status(scout_order)
    # THEN it should pick out the family
    assert len(data['families']) == 1
    family = data['families'][0]
    assert family['name'] == '17093'
    assert family['priority'] == 'standard'
    assert set(family['panels']) == {'IEM', 'EP'}
    assert len(family['samples']) == 3

    first_sample = family['samples'][0]
    assert first_sample['name'] == '17093-I-2A'
    assert first_sample['application'] == 'WGTPCFC030'
    assert first_sample['sex'] == 'female'
    assert first_sample['status'] == 'affected'
    assert first_sample['mother'] == '17093-II-2U'
    assert first_sample['father'] == '17093-II-1U'

    # ... second sample has a comment
    assert isinstance(family['samples'][1]['comment'], str)


def test_store_rml(orders_api, base_store, rml_status_data):

    # GIVEN a basic store with no samples and a rml order
    assert base_store.pools(customer=None).count() == 0
    # WHEN storing the order
    new_pools = orders_api.store_pools(
        customer=rml_status_data['customer'],
        order=rml_status_data['order'],
        ordered=dt.datetime.now(),
        ticket=1234348,
        pools=rml_status_data['pools'],
    )
    # THEN it should update the database with new pools
    assert len(new_pools) == 1
    assert base_store.pools(customer=None).count() == 1
    new_pool = base_store.pools(customer=None).first()
    assert new_pool == new_pools[0]
    assert new_pool.name == '1'
    assert new_pool.application_version.application.tag == 'RMLS05R150'
    assert new_pool.capture_kit == 'Agilent Sureselect CRE'
    # ... and add a delivery
    assert len(new_pool.deliveries) == 1
    assert new_pool.deliveries[0].destination == 'caesar'


def test_store_rml_bad_apptag(orders_api, base_store, rml_status_data):

    # GIVEN a basic store with no samples and a rml order
    assert base_store.pools(customer=None).count() == 0

    for pool in rml_status_data['pools']:
        pool['application'] = 'nonexistingtag'

    # THEN it should raise OrderError
    with pytest.raises(OrderError):
        # WHEN storing the order
        new_pools = orders_api.store_pools(
            customer=rml_status_data['customer'],
            order=rml_status_data['order'],
            ordered=dt.datetime.now(),
            ticket=1234348,
            pools=rml_status_data['pools'],
        )


def test_store_samples(orders_api, base_store, fastq_status_data):
    # GIVEN a basic store with no samples and a fastq order
    assert base_store.samples().count() == 0
    assert base_store.families().count() == 0

    # WHEN storing the order
    new_samples = orders_api.store_fastq_samples(
        customer=fastq_status_data['customer'],
        order=fastq_status_data['order'],
        ordered=dt.datetime.now(),
        ticket=1234348,
        samples=fastq_status_data['samples'],
    )

    # THEN it should store the samples and create a "fake" family for
    # the non-tumour sample
    assert len(new_samples) == 2
    assert base_store.samples().count() == 2
    assert base_store.families().count() == 1
    first_sample = new_samples[0]
    assert len(first_sample.links) == 1
    family_link = first_sample.links[0]
    assert family_link.family == base_store.families().first()
    for sample in new_samples:
        assert len(sample.deliveries) == 1


def test_store_samples_bad_apptag(orders_api, base_store, fastq_status_data):
    # GIVEN a basic store with no samples and a fastq order
    assert base_store.samples().count() == 0
    assert base_store.families().count() == 0

    for sample in fastq_status_data['samples']:
        sample['application'] = 'nonexistingtag'

    # THEN it should raise OrderError
    with pytest.raises(OrderError):
        # WHEN storing the order
        new_samples = orders_api.store_fastq_samples(
            customer=fastq_status_data['customer'],
            order=fastq_status_data['order'],
            ordered=dt.datetime.now(),
            ticket=1234348,
            samples=fastq_status_data['samples'],
        )


def test_store_microbial_samples(orders_api, base_store,  microbial_status_data):

    # GIVEN a basic store with no samples and a microbial order
    assert base_store.microbial_samples().count() == 0
    assert base_store.microbial_orders().count() == 0

    # WHEN storing the order
    new_order = orders_api.store_microbial_order(
        customer=microbial_status_data['customer'],
        order=microbial_status_data['order'],
        ordered=dt.datetime.now(),
        ticket=1234348,
        lims_project='dummy_lims_project',
        samples=microbial_status_data['samples'],
    )

    # THEN it should store the samples
    assert len(new_order.microbial_samples) == 5
    assert base_store.microbial_samples().count() == 5
    assert base_store.microbial_orders().count() == 1


def test_store_microbial_samples_bad_apptag(orders_api, base_store,  microbial_status_data):

    # GIVEN a basic store with no samples and a microbial order
    assert base_store.microbial_samples().count() == 0
    assert base_store.microbial_orders().count() == 0

    for sample in microbial_status_data['samples']:
        sample['application'] = 'nonexistingtag'

    # THEN it should raise OrderError
    with pytest.raises(OrderError):
        # WHEN storing the order
        new_order = orders_api.store_microbial_order(
            customer=microbial_status_data['customer'],
            order=microbial_status_data['order'],
            ordered=dt.datetime.now(),
            ticket=1234348,
            lims_project='dummy_lims_project',
            samples=microbial_status_data['samples'],
        )


def test_store_microbial_sample_priority(orders_api, base_store, microbial_status_data):

    # GIVEN a basic store with no samples
    assert base_store.microbial_samples().count() == 0

    # WHEN storing the order
    orders_api.store_microbial_order(
        customer=microbial_status_data['customer'],
        order=microbial_status_data['order'],
        ordered=dt.datetime.now(),
        ticket=1234348,
        lims_project='dummy_lims_project',
        samples=microbial_status_data['samples'],
    )

    # THEN it should store the sample priority
    microbial_sample = base_store.microbial_samples().first()

    assert microbial_sample.priority_human == 'research'


def test_store_families(orders_api, base_store, scout_status_data):
    # GIVEN a basic store with no samples or nothing in it + scout order
    assert base_store.samples().first() is None
    assert base_store.families().first() is None

    # WHEN storing the order
    new_families = orders_api.store_families(
        customer=scout_status_data['customer'],
        order=scout_status_data['order'],
        ordered=dt.datetime.now(),
        ticket=1234567,
        families=scout_status_data['families'],
    )

    # THEN it should create and link samples and the family
    family_obj = base_store.families().first()
    assert len(new_families) == 1
    new_family = new_families[0]
    assert new_family == family_obj
    assert new_family.name == '17093'
    assert set(new_family.panels) == {'IEM', 'EP'}
    assert new_family.priority_human == 'standard'

    assert len(new_family.links) == 3
    new_link = new_family.links[0]
    assert new_link.status == 'affected'
    assert new_link.mother.name == '17093-II-2U'
    assert new_link.father.name == '17093-II-1U'
    assert new_link.sample.name == '17093-I-2A'
    assert new_link.sample.sex == 'female'
    assert new_link.sample.application_version.application.tag == 'WGTPCFC030'
    assert isinstance(new_family.links[1].sample.comment, str)

    assert base_store.deliveries().count() == base_store.samples().count()
    for link in new_family.links:
        assert len(link.sample.deliveries) == 1


def test_store_families_bad_apptag(orders_api, base_store, scout_status_data):
    # GIVEN a basic store with no samples or nothing in it + scout order
    assert base_store.samples().first() is None
    assert base_store.families().first() is None

    for family in scout_status_data['families']:
        for sample in family['samples']:
            sample['application'] = 'nonexistingtag'

    # THEN it should raise OrderError
    with pytest.raises(OrderError):
        # WHEN storing the order
        new_families = orders_api.store_families(
            customer=scout_status_data['customer'],
            order=scout_status_data['order'],
            ordered=dt.datetime.now(),
            ticket=1234567,
            families=scout_status_data['families'],
        )


def test_store_external(orders_api, base_store, external_status_data):

    # GIVEN a basic store with no samples or nothing in it + external order
    assert base_store.samples().first() is None
    assert base_store.families().first() is None

    # WHEN storing the order
    new_families = orders_api.store_families(
        customer=external_status_data['customer'],
        order=external_status_data['order'],
        ordered=dt.datetime.now(),
        ticket=1234567,
        families=external_status_data['families'],
    )

    # THEN it should create and link samples and the family
    family_obj = base_store.families().first()
    assert len(new_families) == 2
    new_family = new_families[1]
    assert new_family == family_obj
    assert new_family.name == 'F0009704'
    assert set(new_family.panels) == set(['SKD'])
    assert new_family.priority_human == 'standard'

    assert len(new_family.links) == 1
    new_link = new_family.links[0]
    assert new_link.status == 'affected'
    assert new_link.sample.name == '2016-20204'
    assert new_link.sample.sex == 'female'
    assert new_link.sample.capture_kit == 'Twist_Target_hg19.bed'
    assert new_link.sample.application_version.application.tag == 'EXXCUSR000'
    assert isinstance(new_family.links[0].sample.comment, str)

    assert base_store.deliveries().count() == base_store.samples().count()
    for link in new_family.links:
        assert len(link.sample.deliveries) == 1


def test_store_external_bad_apptag(orders_api, base_store, external_status_data):

    # GIVEN a basic store with no samples or nothing in it + external order
    assert base_store.samples().first() is None
    assert base_store.families().first() is None

    for family in external_status_data['families']:
        for sample in family['samples']:
            sample['application'] = 'nonexistingtag'

    # THEN it should raise OrderError
    with pytest.raises(OrderError):
        # WHEN storing the order
        new_families = orders_api.store_families(
            customer=external_status_data['customer'],
            order=external_status_data['order'],
            ordered=dt.datetime.now(),
            ticket=1234567,
            families=external_status_data['families'],
        )
