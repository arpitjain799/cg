import logging
from pathlib import Path
from typing import Dict, List, Optional

from cg.apps.orderform.schemas.orderform_schema import OrderCase, OrderformSchema, OrderSample
from cg.exc import OrderFormError

LOG = logging.getLogger(__name__)


class OrderformParser:
    """Class to parse orderforms"""

    def __init__(self):
        self.samples: List[OrderSample] = []
        self.project_type: Optional[str] = None
        self.delivery_type: Optional[str] = None
        self.customer_id: Optional[str] = None
        self.order_comment: Optional[str] = None
        self.order_name: Optional[str] = None

    def parse_orderform(self, orderform_file: Path) -> None:
        """Parse the orderform information"""
        raise NotImplementedError

    def group_cases(self) -> Dict[str, List[OrderSample]]:
        """Group samples in cases."""
        LOG.info("Group samples under respective case")
        cases = {}
        for sample in self.samples:
            case_id = sample.case_id
            if not case_id:
                continue
            if case_id not in cases:
                cases[case_id] = []
            cases[case_id].append(sample)
        LOG.info("Found cases %s", cases.keys())
        return cases

    def expand_case(self, case_id: str, case_samples: List[OrderSample]) -> OrderCase:
        """Fill-in information about case."""

        priorities = {sample.priority for sample in case_samples if sample.priority}
        if len(priorities) != 1:
            raise OrderFormError(f"multiple values for 'Priority' for case: {case_id}")

        gene_panels = set()
        for sample in self.samples:
            if not sample.panels:
                continue
            gene_panels.update(set(sample.panels))

        return OrderCase(
            name=case_id,
            samples=case_samples,
            require_qcok=any(sample.require_qcok for sample in case_samples),
            priority=priorities.pop(),
            panels=list(gene_panels),
        )

    def generate_orderform(self) -> OrderformSchema:
        """Generate an orderform"""
        cases_map: Dict[str, List[OrderSample]] = self.group_cases()
        case_objs: List[OrderCase] = []
        for case_id in cases_map:
            case_objs.append(self.expand_case(case_id=case_id, case_samples=cases_map[case_id]))
        return OrderformSchema(
            comment=self.order_comment,
            samples=self.samples,
            cases=case_objs,
            name=self.order_name,
            customer=self.customer_id,
            delivery_type=self.delivery_type,
            project_type=self.project_type,
        )

    def __repr__(self):
        return (
            f"OrderformParser(project_type={self.project_type},delivery_type={self.delivery_type},customer_id="
            f"{self.customer_id},order_name={self.order_name})"
        )
