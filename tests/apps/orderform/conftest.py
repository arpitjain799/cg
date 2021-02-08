"""Fixtures for the orderform tests"""

import pytest


@pytest.fixture(name="rml_sample")
def fixture_rml_sample() -> dict:
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
