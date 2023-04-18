"""Handler to delete data objects"""

from typing import List

from cg.store.filters.status_flow_cell_filters import apply_flow_cell_filter, FlowCellFilter
from cg.store.models import Flowcell, Family, Sample
from cg.store.api.base import BaseHandler


class DeleteDataHandler(BaseHandler):
    """Contains methods to delete business data model instances"""

    def delete_flow_cell(self, flow_cell_id: str) -> None:
        """Delete flow cell."""
        flow_cell: Flowcell = apply_flow_cell_filter(
            flow_cells=self._get_query(table=Flowcell),
            flow_cell_name=flow_cell_id,
            filter_functions=[FlowCellFilter.GET_BY_NAME],
        ).first()

        if flow_cell:
            flow_cell.delete()
            flow_cell.flush()
            self.commit()

    def delete_relationships_sample(self, sample: Sample) -> None:
        """Delete relationships between all cases and the provided sample."""
        if sample and sample.links:
            for case_sample in sample.links:
                case_sample.delete()
            self.commit()

    def delete_cases_without_samples(self, case_internal_ids: List[str]) -> None:
        """Delete any cases specified in case_ids without samples."""
        for case_internal_id in case_internal_ids:
            case: Family = self.get_case_by_internal_id(internal_id=case_internal_id)
            if case and not case.links:
                case.delete()
        self.commit()
