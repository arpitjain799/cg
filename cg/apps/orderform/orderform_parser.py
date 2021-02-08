from pathlib import Path
from typing import Dict, List, Set

from cg.apps.lims.orderform import CASE_PROJECT_TYPES
from cg.apps.orderform.orderform_schema import OrderformSchema, OrderSample
from cg.constants import DataDelivery, Pipeline
from cg.exc import OrderFormError
from cg.meta.orders import OrderType
from cg.meta.orders.status import StatusHandler


class OrderformParser:
    """Class to parse orderforms"""

    ACCEPTED_DATA_ANALYSES: List[str] = [
        str(Pipeline.MIP_DNA),
        str(Pipeline.FLUFFY),
        str(Pipeline.BALSAMIC),
    ]
    NO_VALUE = "no_value"

    def __init__(self):
        pass

    def parse_orderform(self, orderform_file: Path) -> OrderformSchema:
        raise NotImplementedError

    @staticmethod
    def group_cases(samples: List[OrderSample]) -> Dict[str, List[OrderSample]]:
        """Group samples in cases."""
        cases = {}
        for sample in samples:
            case_id = sample.family_name
            if case_id not in cases:
                cases[case_id] = []
            cases[case_id].append(sample)
        return cases

    def get_project_type(self, samples: List[OrderSample]) -> str:
        """Determine the project type."""

        data_analyses: Set[str] = {sample.data_analysis for sample in samples}

        if len(data_analyses) > 1:
            raise OrderFormError(f"mixed 'Data Analysis' types: {', '.join(data_analyses)}")

        data_analysis: str = samples[0].data_analysis
        if data_analysis in self.ACCEPTED_DATA_ANALYSES:
            return data_analysis

        raise OrderFormError(f"Unsupported order_data orderform: {data_analysis}")


class JsonOrderformParser(OrderformParser):
    ACCEPTED_DATA_ANALYSES: List[str] = [
        str(Pipeline.MIP_DNA),
        str(Pipeline.FLUFFY),
        str(Pipeline.BALSAMIC),
    ]
    NO_VALUE = "no_value"

    @staticmethod
    def project_type_to_order_type(project_type: OrderType) -> str:
        """In the case where data delivery was not defined we map from project type"""
        project_to_order = {
            OrderType.METAGENOME: DataDelivery.FASTQ,
            OrderType.FASTQ: DataDelivery.FASTQ,
            OrderType.RML: DataDelivery.FASTQ,
            OrderType.MIP_RNA: DataDelivery.ANALYSIS_FILES,
            OrderType.FLUFFY: DataDelivery.NIPT_VIEWER,
        }
        if project_type not in project_to_order:
            raise OrderFormError(f"Could not find data delivery for: {project_type}")
        return project_to_order[project_type]

    def get_data_delivery(self, samples: List[OrderSample], project_type: OrderType) -> str:
        """Determine the order_data delivery type."""

        data_deliveries = {sample.data_delivery for sample in samples}

        if len(data_deliveries) > 1:
            raise OrderFormError(f"mixed 'Data Delivery' types: {', '.join(data_deliveries)}")

        data_delivery = samples[0].data_delivery

        if data_delivery == self.NO_VALUE:
            return str(self.project_type_to_order_type(project_type))

        try:
            return str(DataDelivery(data_delivery))
        except ValueError:
            raise OrderFormError(f"Unsupported order_data delivery: {data_delivery}")

    @staticmethod
    def expand_case(case_id: str, parsed_case: dict) -> dict:
        """Fill-in information about families."""
        new_case = {"name": case_id, "samples": []}
        samples = parsed_case

        # Loop over all samples and check if any of them have require qcok: True
        require_qcoks = set(raw_sample["require_qcok"] for raw_sample in samples)
        new_case["require_qcok"] = True in require_qcoks

        # Loop over all samples of a case and check if they have the same priority
        priorities = set(raw_sample["priority"].lower() for raw_sample in samples)
        if len(priorities) != 1:
            raise OrderFormError(f"multiple values for 'Priority' for case: {case_id}")
        new_case["priority"] = priorities.pop()

        gene_panels = set()
        # add all panels found from all individuals in case
        for raw_sample in samples:
            if raw_sample.get("panels"):
                gene_panels.update(raw_sample["panels"])

            new_sample = {}

            # Add random keys? There is no controll over what is added here
            for key, value in raw_sample.items():
                if key not in ["panels", "well_position"]:
                    new_sample[key] = value

            # Add the well position
            well_position_raw = raw_sample.get("well_position")
            if well_position_raw:
                new_sample["well_position"] = (
                    ":".join(well_position_raw)
                    if ":" not in well_position_raw
                    else well_position_raw
                )

            new_case["samples"].append(new_sample)

        # Add panels to case
        if gene_panels:
            new_case["panels"] = list(gene_panels)

        return new_case

    def parse_orderform(self, order_data: dict) -> OrderformSchema:
        """Parse order form in JSON format."""

        orderform: OrderformSchema = OrderformSchema(**order_data)
        return orderform

        project_type = self.get_project_type(orderform.samples)
        data_delivery = self.get_data_delivery(
            samples=orderform.samples, project_type=OrderType(project_type)
        )
        customer_id = order_data["customer"].lower()
        comment = order_data.get("comment")
        order_name = order_data.get("name")

        if project_type in CASE_PROJECT_TYPES:
            # Group the samples under there case
            parsed_cases = StatusHandler.group_cases(orderform.samples)
            items = []
            for case_id, parsed_case in parsed_cases.items():
                case_data = self.expand_case(case_id, parsed_case)
                items.append(case_data)
        else:
            items = orderform.samples

        parsed_order = {
            "comment": comment,
            "customer": customer_id,
            "delivery_type": str(data_delivery),
            "items": items,
            "name": order_name,
            "project_type": project_type,
        }

        return parsed_order
