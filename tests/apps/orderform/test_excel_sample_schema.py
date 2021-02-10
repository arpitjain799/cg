import pytest
from cg.apps.orderform.schemas.excel_sample_schema import ExcelSample
from cg.constants import DataDelivery
from pydantic import ValidationError


def test_excel_minimal_sample_schema(minimal_excel_sample: dict):
    """Test instantiate a minimal sample"""
    # GIVEN some simple sample info from the simplest sample possible

    # WHEN creating a excel sample
    excel_sample: ExcelSample = ExcelSample(**minimal_excel_sample)

    # THEN assert that the sample name info was correctly parsed
    assert excel_sample.name == minimal_excel_sample["Sample/Name"]


def test_excel_swedish_priority(minimal_excel_sample: dict):
    """Test instantiate a sample with swedish priority"""
    # GIVEN some sample where the priority is in swedish
    minimal_excel_sample["UDF/priority"] = "förtur"

    # WHEN creating a excel sample
    excel_sample: ExcelSample = ExcelSample(**minimal_excel_sample)

    # THEN assert that the sample priority info was correctly parsed
    assert excel_sample.priority == "priority"


def test_excel_source_type(minimal_excel_sample: dict):
    """Test instantiate a sample with source type"""
    # GIVEN some sample with a known source type
    source_type = "blood"
    minimal_excel_sample["UDF/Source"] = source_type

    # WHEN creating a excel sample
    excel_sample: ExcelSample = ExcelSample(**minimal_excel_sample)

    # THEN assert that the source type info was correctly parsed
    assert excel_sample.source == source_type


def test_excel_unknown_source_type(minimal_excel_sample: dict):
    """Test instantiate a sample with a unknown source type

    ValidationError should be raised since the source type does not exist
    """
    # GIVEN some sample with a known source type
    source_type = "flagalella"
    minimal_excel_sample["UDF/Source"] = source_type

    # WHEN creating a excel sample
    with pytest.raises(ValidationError):
        # THEN assert that a validation error is raised since source does not exist
        excel_sample: ExcelSample = ExcelSample(**minimal_excel_sample)


def test_excel_with_panels(minimal_excel_sample: dict):
    """Test instantiate a sample with some gene panels set"""
    # GIVEN some sample with two gene panels in a semi colon separated string
    panel_1 = "OMIM"
    panel_2 = "PID"
    minimal_excel_sample["UDF/Gene List"] = ";".join([panel_1, panel_2])
    print(minimal_excel_sample)

    # WHEN creating a excel sample
    excel_sample: ExcelSample = ExcelSample(**minimal_excel_sample)

    # THEN assert that the panels was parsed into a list
    assert set(excel_sample.panels) == set([panel_1, panel_2])


def test_mip_sample_is_correct(mip_orderform_sample: dict):
    """Tests that a mip sample is parsed correct"""
    # GIVEN sample data about a known sample

    # WHEN parsing the sample
    proband_sample: ExcelSample = ExcelSample(**mip_orderform_sample)
    assert proband_sample.name == "s1"
    assert proband_sample.container == "96 well plate"
    assert proband_sample.data_analysis == "MIP DNA"
    assert proband_sample.data_delivery == str(DataDelivery.SCOUT)
    assert proband_sample.application == "PANKTTR010"
    assert proband_sample.sex == "male"
    assert proband_sample.source == "tissue (FFPE)"
    assert proband_sample.tumour is True
    assert proband_sample.container_name == "plate1"
    assert proband_sample.well_position == "A:1"
    assert proband_sample.status == "affected"
    assert proband_sample.mother == "s2"
    assert proband_sample.father == "s3"
    assert proband_sample.quantity == "4"
    assert proband_sample.comment == "other Elution buffer"


def test_rml_sample_is_correct(rml_excel_sample: dict):
    """Test that one of the rml samples is on the correct format"""
    # GIVEN a sample with known values
    sample_obj: ExcelSample = ExcelSample(**rml_excel_sample)

    # WHEN fetching the sample

    # THEN assert that all the known values are correct
    assert sample_obj.pool == "pool1"
    assert sample_obj.application == "RMLP10R300"
    assert sample_obj.data_analysis == "FLUFFY"
    assert sample_obj.volume == "1"
    assert sample_obj.concentration == "2"
    assert sample_obj.index == "IDT DupSeq 10 bp Set B"
    assert sample_obj.index_number == "1"

    assert sample_obj.container_name is None
    assert sample_obj.rml_plate_name == "plate"
    assert sample_obj.well_position is None
    assert sample_obj.well_position_rml == "A:1"

    assert sample_obj.reagent_label == "A01 IDT_10nt_541 (ATTCCACACT-AACAAGACCA)"

    assert sample_obj.custom_index == "GATACA"

    assert sample_obj.comment == "comment"
    assert sample_obj.concentration_sample == "3"


def test_tumor_sample_schema(tumor_fastq_sample: dict):
    """Test to validate a tumor fastq sample"""
    # GIVEN some simple sample info from a fastq tumor sample

    # WHEN creating a excel sample
    excel_sample: ExcelSample = ExcelSample(**tumor_fastq_sample)

    # THEN assert that sample information was correctly parsed
    assert excel_sample.tumour is True
    assert excel_sample.source == "tissue (FFPE)"
    assert excel_sample.quantity == "4"
    assert excel_sample.comment == "other Elution buffer"
    assert excel_sample.tumour is True


def test_normal_sample_schema(normal_fastq_sample: dict):
    """Test to validate a normal fastq sample"""
    # GIVEN some simple sample info from a fastq normal sample

    # WHEN creating a excel sample
    excel_sample: ExcelSample = ExcelSample(**normal_fastq_sample)

    # THEN assert that the sample information was correctly parsed
    assert excel_sample.container == "Tube"
    assert excel_sample.data_analysis == "No analysis"
    assert excel_sample.data_delivery == "fastq"
    assert excel_sample.application == "WGTPCFC030"
    assert excel_sample.sex == "female"
    assert excel_sample.case_id == "c1"
    assert excel_sample.require_qcok is False
    assert excel_sample.source == "bone marrow"
    assert excel_sample.priority == "research"
    assert excel_sample.container_name == ""
    assert excel_sample.well_position == ""
    assert excel_sample.tumour is False
