from cg.apps.orderform.order_schema import ExcelSample


def test_excel_sample_schema_simple_rml(rml_sample: dict):
    """Test a basic rml sample"""
    # GIVEN some simple sample info from a RML sample

    # WHEN creating a excel sample
    excel_sample: ExcelSample = ExcelSample(**rml_sample)

    # THEN assert that the sample priority info was correctly parsed
    assert excel_sample.priority == rml_sample["UDF/priority"]
