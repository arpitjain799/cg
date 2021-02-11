from cg.apps.lims import orderform
from cg.constants import DataDelivery, Pipeline


def test_parsing_metagenome_orderform(metagenome_orderform):

    # GIVEN an orderform for one metagenome sample
    # WHEN parsing the file
    data = orderform.parse_orderform(metagenome_orderform)

    # THEN it should detect the project type
    assert data["project_type"] == "metagenome"
    # ... and find all samples
    assert len(data["items"]) == 19
    # ... and collect relevant sample info
    sample = data["items"][0]

    assert sample["name"] == "sample1"
    assert sample["source"] == "other"
    assert sample["data_analysis"].lower() == str(Pipeline.FASTQ)
    assert sample["application"] == "METPCFR030"
    assert sample["customer"] == "cust000"
    assert sample["require_qcok"] is True
    assert sample["elution_buffer"] == 'Other (specify in "Comments")'
    assert sample["extraction_method"] == "other (specify in comment field)"
    assert sample["container"] == "96 well plate"
    assert sample["priority"] == "research"

    # Required if Plate
    assert sample["container_name"] == "plate1"
    assert sample["well_position"] == "A:1"

    # These fields are not required
    assert sample["concentration_sample"] == "1"
    assert sample["quantity"] == "2"
    assert sample["comment"] == "comment"


def test_parsing_microbial_orderform(microbial_orderform):
    # GIVEN a path to a microbial orderform with 3 samples

    # WHEN parsing the file
    data = orderform.parse_orderform(microbial_orderform)

    # THEN it should determine the type of project and customer
    assert data["project_type"] == str(Pipeline.MICROSALT)
    assert data["customer"] == "cust000"

    # ... and find all samples
    assert len(data["items"]) == 14

    # ... and collect relevant sample data
    sample_data = data["items"][0]

    assert sample_data["name"] == "s1"
    assert sample_data.get("internal_id") is None
    assert sample_data["organism"] == "other"
    assert sample_data["reference_genome"] == "NC_00001"
    assert sample_data["data_analysis"].lower() == str(Pipeline.FASTQ)
    assert sample_data["application"] == "MWRNXTR003"
    # customer on order (data)
    assert sample_data["require_qcok"] is True
    assert sample_data["elution_buffer"] == 'Other (specify in "Comments")'
    assert sample_data["extraction_method"] == "other (specify in comment field)"
    assert sample_data["container"] == "96 well plate"
    assert sample_data.get("priority") in "research"

    assert sample_data["container_name"] == "plate1"
    assert sample_data["well_position"] == "A:1"

    assert sample_data["organism_other"] == "other species"

    assert sample_data["concentration_sample"] == "1"
    assert sample_data["quantity"] == "2"
    assert sample_data["comment"] == "comment"


def test_parsing_balsamic_orderform(balsamic_orderform):

    # GIVEN an order form for a cancer order with 11 samples,
    # WHEN parsing the order form
    data = orderform.parse_orderform(balsamic_orderform)

    # THEN it should detect the type of project
    assert data["project_type"] == str(Pipeline.BALSAMIC)

    # ... and it should find and group all samples in case
    assert len(data["items"]) == 36

    # ... and collect relevant data about the case
    # ... and collect relevant info about the samples

    case = data["items"][0]
    sample = case["samples"][0]
    assert len(case["samples"]) == 2

    # This information is required

    assert sample["name"] == "s1"
    assert sample["container"] == "96 well plate"
    assert sample["data_analysis"].lower() == str(Pipeline.BALSAMIC)
    assert sample["data_delivery"] == str(DataDelivery.ANALYSIS_BAM_FILES)
    assert sample["application"] == "PANKTTR010"
    assert sample["sex"] == "male"
    assert case["name"] == "c1"
    assert data["customer"] == "cust000"
    assert case["require_qcok"] is True
    assert sample["volume"] == "1"
    assert sample["source"] == "tissue (FFPE)"
    assert case["priority"] == "research"

    # Required if Plate
    assert sample["container_name"] == "plate1"
    assert sample["well_position"] == "A:1"

    # This information is required for panel- or exome analysis
    assert sample["elution_buffer"] == 'Other (specify in "Comments")'

    # This information is required for Balsamic analysis (cancer)
    assert sample["tumour"] is True
    assert sample["capture_kit"] == "GMCKsolid"
    assert sample["tumour_purity"] == "5"

    assert sample["formalin_fixation_time"] == "2"
    assert sample["post_formalin_fixation_time"] == "3"
    assert sample["tissue_block_size"] == "small"

    # This information is optional
    assert sample["quantity"] == "4"
    assert sample["comment"] == "other Elution buffer"


def test_parsing_mip_rna_orderform(mip_rna_orderform):

    # GIVEN an order form for a mip balsamic order with 3 samples, 1 trio, in a plate
    # WHEN parsing the order form
    data = orderform.parse_orderform(mip_rna_orderform)

    # THEN it should detect the type of project
    assert data["project_type"] == str(Pipeline.MIP_RNA)
    assert data["customer"] == "cust000"
    # ... and it should find and group all samples in cases
    assert len(data["items"]) == 12
    # ... and collect relevant data about the cases
    first_case = data["items"][0]
    assert len(first_case["samples"]) == 3
    assert first_case["name"] == "c1"
    assert first_case["priority"] == "research"
    assert set(first_case["panels"]) == set()
    assert first_case["require_qcok"] is True
    # ... and collect relevant info about the samples

    first_sample = first_case["samples"][0]
    assert first_sample["name"] == "s1"
    assert first_sample["container"] == "96 well plate"
    assert first_sample["data_analysis"] == "MIP RNA"
    assert first_sample["data_delivery"].lower() == str(DataDelivery.ANALYSIS_FILES)
    assert first_sample["application"] == "RNAPOAR025"
    assert first_sample["sex"] == "male"
    # case-id on the case
    # customer on the order (data)
    # require-qc-ok on the case
    assert first_sample["source"] == "tissue (FFPE)"

    assert first_sample["container_name"] == "plate1"
    assert first_sample["well_position"] == "A:1"

    assert first_sample["tumour"] is True

    assert first_sample["quantity"] == "4"
    assert first_sample["comment"] == "other Elution buffer"

    # required for RNA samples
    assert first_sample["from_sample"] == "s1"
    assert first_sample["time_point"] == "0"
