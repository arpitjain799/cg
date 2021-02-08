from cg.apps.orderform.orderform_parser import JsonOrderformParser
from cg.apps.orderform.orderform_schema import OrderformSchema


def test_parse_rml_orderform(rml_order_to_submit: dict):
    """Test to parse the RML orderform"""
    # GIVEN a orderform API
    order_form_parser = JsonOrderformParser()

    # WHEN parsing the RML orderform
    order: OrderformSchema = order_form_parser.parse_orderform(order_data=rml_order_to_submit)

    # THEN assert that the orderform was parsed in the correct way
    assert isinstance(order, OrderformSchema)
