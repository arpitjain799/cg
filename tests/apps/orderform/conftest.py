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


@pytest.fixture(name="fastq_order_parser")
def fixture_fastq_order_parser(fastq_orderform: str) -> ExcelOrderformParser:
    """Return a orderform parser that have parsed an orderform in excel format"""
    order_form_parser = ExcelOrderformParser()
    order_form_parser.parse_orderform(excel_path=fastq_orderform)
    return order_form_parser


@pytest.fixture(name="nr_samples_rml_orderform")
def fixture_nr_samples_rml_orderform(rml_orderform: str) -> int:
    """Return the number of samples in the rml orderform"""
    return 26


@pytest.fixture(name="nr_samples_fastq_orderform")
def fixture_nr_samples_fastq_orderform(fastq_orderform: str) -> int:
    """Return the number of samples in the rml orderform"""
    return 36


@pytest.fixture(name="tumor_fastq_sample")
def fixture_tumor_fastq_sample() -> dict:
    """Return a parsed tumor sample in excel format"""
    return {
        "Sample/Name": "s1",
        "UDF/customer": "cust000",
        "UDF/Data Analysis": "No analysis",
        "UDF/Data Delivery": "fastq",
        "UDF/Sequencing Analysis": "EXOKTTR020",
        "UDF/familyID": "c1",
        "UDF/Gender": "M",
        "UDF/tumor": "yes",
        "UDF/Source": "tissue (FFPE)",
        "UDF/priority": "research",
        "UDF/Process only if QC OK": "yes",
        "UDF/Volume (uL)": "1",
        "Container/Type": "96 well plate",
        "Container/Name": "plate1",
        "Sample/Well Location": "A:1",
        "UDF/Gene List": "",
        "UDF/Status": "",
        "UDF/motherID": "",
        "UDF/fatherID": "",
        "UDF/is_for_sample": "",
        "UDF/time_point": "",
        "UDF/Capture Library version": "GMCKsolid",
        "UDF/Sample Buffer": 'Other (specify in "Comments")',
        "UDF/Formalin Fixation Time": "2",
        "UDF/Post Formalin Fixation Time": "3",
        "UDF/Tissue Block Size": "small",
        "UDF/Quantity": "4",
        "UDF/tumour purity": "5",
        "UDF/Comment": "other Elution buffer",
    }


@pytest.fixture(name="normal_fastq_sample")
def fixture_normal_fastq_sample() -> dict:
    """Return a parsed normal sample from a fastq orderform in excel format"""
    return {
        "Sample/Name": "s2",
        "UDF/customer": "cust000",
        "UDF/Data Analysis": "No analysis",
        "UDF/Data Delivery": "fastq",
        "UDF/Sequencing Analysis": "WGTPCFC030",
        "UDF/familyID": "c1",
        "UDF/Gender": "F",
        "UDF/tumor": "no",
        "UDF/Source": "bone marrow",
        "UDF/priority": "research",
        "UDF/Process only if QC OK": "no",
        "UDF/Volume (uL)": "1",
        "Container/Type": "Tube",
        "Container/Name": "",
        "Sample/Well Location": "",
        "UDF/Gene List": "",
        "UDF/Status": "",
        "UDF/motherID": "",
        "UDF/fatherID": "",
        "UDF/is_for_sample": "",
        "UDF/time_point": "",
        "UDF/Capture Library version": "",
        "UDF/Sample Buffer": "",
        "UDF/Formalin Fixation Time": "",
        "UDF/Post Formalin Fixation Time": "",
        "UDF/Tissue Block Size": "",
        "UDF/Quantity": "",
        "UDF/tumour purity": "",
        "UDF/Comment": "",
    }


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
