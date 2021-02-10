from pathlib import Path
from typing import Optional

from cg.apps.orderform.excel_orderform_parser import ExcelOrderformParser
from cg.apps.orderform.schemas.excel_sample_schema import ExcelSample
from cg.apps.orderform.schemas.orderform_schema import OrderformSchema
from cg.constants import Pipeline


def get_sample_obj(
    order_form_parser: ExcelOrderformParser, sample_id: str
) -> Optional[ExcelSample]:
    for sample_obj in order_form_parser.samples:
        if sample_obj.name == sample_id:
            return sample_obj


def test_parse_rml_orderform(rml_orderform: str, nr_samples_rml_orderform: int):
    """Test to parse an excel orderform in xlsx format"""
    # GIVEN a orderform in excel format
    assert Path(rml_orderform).suffix == ".xlsx"
    # GIVEN a orderform API
    order_form_parser = ExcelOrderformParser()
    # GIVEN the correct orderform name
    order_name: str = Path(rml_orderform).stem

    # WHEN parsing the RML orderform
    order_form_parser.parse_orderform(excel_path=rml_orderform)

    # THEN assert that the correct name was set
    assert order_form_parser.order_name == order_name

    # THEN assert that the number of samples was correct
    assert len(order_form_parser.samples) == nr_samples_rml_orderform


def test_parse_fastq_orderform(fastq_orderform: str, nr_samples_fastq_orderform: int):
    """Test to parse an fastq orderform in xlsx format"""
    # GIVEN a orderform in excel format
    assert Path(fastq_orderform).suffix == ".xlsx"
    # GIVEN a orderform API
    order_form_parser = ExcelOrderformParser()
    # GIVEN the correct orderform name
    order_name: str = Path(fastq_orderform).stem

    # WHEN parsing the fastq orderform
    order_form_parser.parse_orderform(excel_path=fastq_orderform)

    # THEN assert that the correct name was set
    assert order_form_parser.order_name == order_name

    # THEN assert that the correct number if samples where parsed
    assert len(order_form_parser.samples) == nr_samples_fastq_orderform

    # THEN it should determine the project type
    assert order_form_parser.project_type == str(Pipeline.FASTQ)

    # THEN it should determine the correct customer should have been parsed
    assert order_form_parser.customer_id == "cust000"


def test_fastq_samples_is_correct(fastq_order_parser: ExcelOrderformParser):
    """Test that everything was correctly parsed from the fastq order"""
    # GIVEN a orderform parser where a fastq order is parsed

    # GIVEN a tumor and normal sample with known information
    tumor_sample_id = "s1"
    normal_sample_id = "s2"

    # WHEN fetching the tumor and the normal sample
    tumour_sample = get_sample_obj(fastq_order_parser, tumor_sample_id)
    normal_sample = get_sample_obj(fastq_order_parser, normal_sample_id)

    # THEN assert that they where both parsed
    assert tumour_sample and normal_sample


def test_generate_parsed_rml_orderform(rml_order_parser: ExcelOrderformParser, caplog):
    """Test to generate a order from a parsed rml excel file"""
    # GIVEN a order form parser that have parsed an excel file

    # WHEN generating the order
    order: OrderformSchema = rml_order_parser.generate_orderform()

    # THEN assert that some samples where parsed and found
    assert order.samples
    # THEN assert that no cases where found since this is an RML order
    assert not order.cases
