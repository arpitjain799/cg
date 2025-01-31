from cg.apps.cgstats.crud import create, find
from cg.apps.cgstats.db.models import Supportparams, Datasource, Flowcell
from cg.apps.cgstats.stats import StatsAPI
from cg.models.demultiplex.demux_results import DemuxResults


def test_create_support_parameters(stats_api: StatsAPI, bcl2fastq_demux_results: DemuxResults):
    # GIVEN a cg stats api without any support parameter for the demux result
    assert not stats_api.find_handler.get_support_parameters_id(
        demux_results=bcl2fastq_demux_results
    )

    # WHEN creating the new support parameters
    create.create_support_parameters(manager=stats_api, demux_results=bcl2fastq_demux_results)

    # THEN assert that the parameters was created
    support_parameters_id = stats_api.find_handler.get_support_parameters_id(
        demux_results=bcl2fastq_demux_results
    )
    assert isinstance(support_parameters_id, int)


def test_create_data_source(stats_api: StatsAPI, bcl2fastq_demux_results: DemuxResults):
    # GIVEN a api with some support parameters
    support_parameters: Supportparams = create.create_support_parameters(
        manager=stats_api, demux_results=bcl2fastq_demux_results
    )
    # GIVEN that there are no data source for the given run
    assert not stats_api.find_handler.get_datasource_id(demux_results=bcl2fastq_demux_results)

    # WHEN creating a new datasource
    create.create_datasource(
        manager=stats_api,
        demux_results=bcl2fastq_demux_results,
        support_parameters_id=support_parameters.supportparams_id,
    )

    # THEN assert that the datasource exists
    assert stats_api.find_handler.get_datasource_id(demux_results=bcl2fastq_demux_results)


def test_create_flowcell(stats_api: StatsAPI, bcl2fastq_demux_results: DemuxResults):
    # GIVEN a api without a flowcell object
    assert not stats_api.find_handler.get_flow_cell_id(
        flowcell_name=bcl2fastq_demux_results.flow_cell.id
    )

    # WHEN creating a new flowcell
    create.create_flowcell(manager=stats_api, demux_results=bcl2fastq_demux_results)

    # THEN assert that the flowcell was created
    assert stats_api.find_handler.get_flow_cell_id(
        flowcell_name=bcl2fastq_demux_results.flow_cell.id
    )


def test_create_demux(stats_api: StatsAPI, bcl2fastq_demux_results: DemuxResults):
    # GIVEN a database with a flowcell and a data source
    support_parameters: Supportparams = create.create_support_parameters(
        manager=stats_api, demux_results=bcl2fastq_demux_results
    )
    flowcell: Flowcell = create.create_flowcell(
        manager=stats_api, demux_results=bcl2fastq_demux_results
    )
    data_source: Datasource = create.create_datasource(
        manager=stats_api,
        demux_results=bcl2fastq_demux_results,
        support_parameters_id=support_parameters.supportparams_id,
    )
    # GIVEN that there is not demux object in the database
    assert not stats_api.find_handler.get_demux_id(flowcell_object_id=flowcell.flowcell_id)

    # WHEN creating a demux object
    create.create_demux(
        manager=stats_api,
        demux_results=bcl2fastq_demux_results,
        flowcell_id=flowcell.flowcell_id,
        datasource_id=data_source.datasource_id,
    )

    # THEN assert that a demux object was created
    assert stats_api.find_handler.get_demux_id(flowcell_object_id=flowcell.flowcell_id)


def test_create_dragen_demux(stats_api: StatsAPI, dragen_demux_results: DemuxResults):
    # GIVEN a database with a flowcell and a data source
    support_parameters: Supportparams = create.create_support_parameters(
        manager=stats_api, demux_results=dragen_demux_results
    )
    flowcell: Flowcell = create.create_flowcell(
        manager=stats_api, demux_results=dragen_demux_results
    )
    data_source: Datasource = create.create_datasource(
        manager=stats_api,
        demux_results=dragen_demux_results,
        support_parameters_id=support_parameters.supportparams_id,
    )
    # GIVEN that there is not demux object in the database
    assert not stats_api.find_handler.get_demux_id(flowcell_object_id=flowcell.flowcell_id)

    # WHEN creating a demux object
    demux_object = create.create_demux(
        manager=stats_api,
        demux_results=dragen_demux_results,
        flowcell_id=flowcell.flowcell_id,
        datasource_id=data_source.datasource_id,
    )

    # THEN assert that a demux object was created
    assert stats_api.find_handler.get_demux_id(
        flowcell_object_id=flowcell.flowcell_id, base_mask=demux_object.basemask
    )
