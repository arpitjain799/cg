import logging
from pathlib import Path

from cg.apps.orderform.excel_orderform_parser import ExcelOrderformParser
from cg.apps.orderform.orderform_schema import OrderformSchema


def test_parse_rml_orderform(rml_orderform: str, caplog):
    """Test to parse an excel orderform in xlsx format"""
    caplog.set_level(logging.DEBUG)
    # GIVEN a orderform in excel format
    assert Path(rml_orderform).suffix == ".xlsx"
    # GIVEN a orderform API
    order_form_parser = ExcelOrderformParser()

    # WHEN parsing the RML orderform
    order: OrderformSchema = order_form_parser.parse_orderform(excel_path=rml_orderform)
    from pprint import pprint as pp

    pp(order)
    print(caplog.text)
    # THEN assert that the orderform was parsed in the correct way
    assert isinstance(order, OrderformSchema)
