import pytest
from cg.apps.orderform.schemas.excel_sample_schema import ExcelSample
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


def test_excel_sample_schema_simple_rml(rml_excel_sample: dict):
    """Test a basic rml sample"""
    # GIVEN some simple sample info from a RML sample

    # WHEN creating a excel sample
    excel_sample: ExcelSample = ExcelSample(**rml_excel_sample)

    # THEN assert that the sample priority info was correctly parsed
    assert excel_sample.priority == rml_excel_sample["UDF/priority"]
