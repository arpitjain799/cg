from cg.apps.lims import orderform
from cg.constants import DataDelivery, Pipeline


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
