"""Fixtures for the orderform tests"""

import pytest
from cg.apps.orderform.excel_orderform_parser import ExcelOrderformParser


@pytest.fixture(name="minimal_excel_sample")
def fixture_minimal_excel_sample() -> dict:
    return {
        "Sample/Name": "missingwell",
        "UDF/Data Analysis": "FLUFFY",
        "UDF/Sequencing Analysis": "RMLP05R800",
        "UDF/customer": "cust000",
    }


@pytest.fixture(name="rml_order_parser")
def fixture_rml_order_parser(rml_orderform: str) -> ExcelOrderformParser:
    """Return a orderform parser that have parsed an orderform in excel format"""
    order_form_parser = ExcelOrderformParser()
    order_form_parser.parse_orderform(excel_path=rml_orderform)
    return order_form_parser


@pytest.fixture(name="nr_samples_rml_orderform")
def fixture_nr_samples_rml_orderform(rml_orderform: str) -> int:
    """Return the number of samples in the rml orderform"""
    return 26


@pytest.fixture(name="rml_excel_sample")
def fixture_rml_excel_sample() -> dict:
    return {
        "Sample/Name": "missingwell",
        "Sample/Reagent Label": "NoIndex",
        "UDF/Comment": "",
        "UDF/Concentration (nM)": "2",
        "UDF/Custom index": "",
        "UDF/Data Analysis": "FLUFFY",
        "UDF/Index number": "26",
        "UDF/Index type": "NoIndex",
        "UDF/RML plate name": "plate",
        "UDF/RML well position": "",
        "UDF/Sample Conc.": "",
        "UDF/Sequencing Analysis": "RMLP05R800",
        "UDF/Volume (uL)": "1",
        "UDF/customer": "cust000",
        "UDF/pool name": "pool24",
        "UDF/priority": "clinical trials",
    }
