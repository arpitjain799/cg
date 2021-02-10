import logging
from pathlib import Path
from typing import Optional

from cg.apps.orderform.excel_orderform_parser import ExcelOrderformParser
from cg.apps.orderform.schemas.excel_sample_schema import ExcelSample
from cg.apps.orderform.schemas.orderform_schema import OrderformSchema
from cg.constants import Pipeline


def test_parse_rml_orderform_correct_name(rml_orderform: str, caplog):
    """Test to parse an excel orderform in xlsx format"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a orderform in excel format
    assert Path(rml_orderform).suffix == ".xlsx"
    # GIVEN a orderform API
    order_form_parser = ExcelOrderformParser()
    # GIVEN the correct oder form name
    order_name: str = Path(rml_orderform).stem

    # WHEN parsing the RML orderform
    order_form_parser.parse_orderform(excel_path=rml_orderform)

    # THEN assert that the correct name was set
    assert order_form_parser.order_name == order_name


def test_all_samples_parsed(rml_order_parser: ExcelOrderformParser, nr_samples_rml_orderform: int):
    """Test that the correct number of samples was parsed from rml order form"""
    # GIVEN a orderform parser with a parsed order form
    # GIVEN that we know how many samples that was included in the orderform

    # WHEN parsing the orderform

    # THEN assert that the number of samples was correct
    assert len(rml_order_parser.samples) == nr_samples_rml_orderform


def test_rml_sample_is_correct(rml_order_parser: ExcelOrderformParser):
    """Test that one of the rml samples is on the correct format"""
    # GIVEN a orderform parser with a parsed order form
    # GIVEN a sample with known values
    sample_id = "sample1"
    sample_obj: Optional[ExcelSample] = None
    for sample in rml_order_parser.samples:
        if sample.name == sample_id:
            sample_obj = sample
    # GIVEN that the sample exists
    assert sample_obj

    # WHEN fetching the sample

    # THEN assert that all the known values are correct
    assert sample_obj.pool == "pool1"
    assert sample_obj.application == "RMLP10R300"
    assert sample_obj.data_analysis == str(Pipeline.FLUFFY)
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


def test_generate_parsed_rml_orderform(rml_order_parser: ExcelOrderformParser, caplog):
    """Test to generate a order from a parsed rml excel file"""
    # GIVEN a order form parser that have parsed an excel file

    # WHEN generating the order
    order: OrderformSchema = rml_order_parser.generate_orderform()

    # THEN assert that some samples where parsed and found
    assert order.samples
    # THEN assert that no cases where found since this is an RML order
    assert not order.cases
