import logging
from typing import List, Optional

import alchy
from sqlalchemy import or_

from cg.apps.cgstats.db.models import (
    Supportparams,
    Datasource,
    Demux,
    Flowcell,
    Project,
    Sample,
    Unaligned,
)
from cg.models.cgstats.stats_sample import StatsSample
from cg.models.demultiplex.demux_results import DemuxResults

LOG = logging.getLogger(__name__)
SAMPLE_PATTERN = "{}\_%"


class FindHandler:
    def get_support_parameters_by_document_path(
        self, document_path: str
    ) -> Optional[Supportparams]:
        """Get support parameters by document path."""

        LOG.debug(f"Searching for support parameters with file {document_path}")

        support_params: Supportparams = Supportparams.query.filter_by(
            document_path=document_path
        ).first()

        if support_params:
            LOG.debug(f"Found support parameters with id {support_params.supportparams_id}")
        else:
            LOG.debug("Support parameters not found")

        return support_params

    def get_datasource_by_document_path(self, document_path: str) -> Optional[Datasource]:
        """Get data source by document path."""
        LOG.debug(f"Search for datasource with file {document_path}")

        datasource: Datasource = Datasource.query.filter_by(document_path=document_path).first()

        if datasource:
            LOG.debug(f"Found datasource with id {datasource.datasource_id}")
        else:
            LOG.debug("Could not find datasource")

        return datasource

    def get_flow_cell_id(self, flowcell_name: str) -> Optional[int]:
        LOG.debug(f"Search for flow cell {flowcell_name}")

        flowcell: Flowcell = self.get_flow_cell_by_name(flowcell_name=flowcell_name)
        if flowcell:
            LOG.debug(f"Found flow cell with id {flowcell.flowcell_id}")
            return flowcell.flowcell_id

        LOG.debug("Could not find flow cell")
        return None

    def get_flow_cell_by_name(self, flowcell_name: str):
        """Get flow cell by name."""
        return Flowcell.query.filter_by(flowcellname=flowcell_name).first()

    def get_demux_id(self, flowcell_object_id: int, base_mask: str = "") -> Optional[int]:
        """Flowcell object id refers to a database object"""
        demux: Demux = self.get_demux_by_flow_cell_id_and_base_mask(
            flowcell_id=flowcell_object_id, base_mask=base_mask
        )
        if demux:
            return demux.demux_id
        return None

    def get_demux_by_flow_cell_id_and_base_mask(
        self, flowcell_id: int, base_mask: str
    ) -> Optional[Demux]:
        """Get demux by flow cell id and base mask."""
        return Demux.query.filter_by(flowcell_id=flowcell_id).filter_by(basemask=base_mask).first()

    def get_project_id(self, project_name: str) -> Optional[int]:
        """Get project id by name."""
        project: Project = self.get_project_by_name(project_name=project_name)

        if project:
            return project.project_id
        return None

    def get_project_by_name(self, project_name: str) -> Optional[Project]:
        """Get project by name."""
        return Project.query.filter_by(projectname=project_name).first()

    def get_sample(self, sample_id: str):
        """Get a unique demux sample."""
        pattern = SAMPLE_PATTERN.format(sample_id)
        return Sample.query.filter(
            or_(Sample.samplename.like(pattern), Sample.samplename == sample_id)
        ).first()

    def get_sample_id(self, sample_id: str, barcode: str) -> Optional[int]:
        """Get sample id by name and barcode."""
        sample: Sample = self.get_sample_by_name_and_barcode(sample_name=sample_id, barcode=barcode)
        if sample:
            return sample.sample_id
        return None

    def get_sample_by_name_and_barcode(self, sample_name: str, barcode: str) -> Optional[Sample]:
        """Get sample by name and barcode."""
        return Sample.query.filter_by(samplename=sample_name).filter_by(barcode=barcode).first()

    def get_unaligned_id(self, sample_id: int, demux_id: int, lane: int) -> Optional[int]:
        """Get unaligned id by sample id, demux id and lane."""
        unaligned: Unaligned = self.get_unaligned_by_sample_id_demux_id_and_lane(
            sample_id=sample_id, demux_id=demux_id, lane=lane
        )
        if unaligned:
            return unaligned.unaligned_id

    def get_unaligned_by_sample_id_demux_id_and_lane(
        self, sample_id: int, demux_id: int, lane: int
    ) -> Optional[Unaligned]:
        """Get unaligned by sample id, demux id and lane."""
        return (
            Unaligned.query.filter_by(sample_id=sample_id)
            .filter_by(demux_id=demux_id)
            .filter_by(lane=lane)
            .first()
        )

    def get_samples(self, flowcell: str, project_name: Optional[str] = None) -> alchy.Query:
        query: alchy.Query = Sample.query.join(Sample.unaligned, Unaligned.demux, Demux.flowcell)
        if project_name:
            query = query.join(Sample.project).filter(Project.projectname == project_name)

        query = query.filter(Flowcell.flowcellname == flowcell)

        return query

    def project_sample_stats(
        self, flowcell: str, project_name: Optional[str] = None
    ) -> List[StatsSample]:
        samples_query: alchy.Query = self.get_samples(flowcell=flowcell, project_name=project_name)
        db_sample: Sample
        return [StatsSample.from_orm(db_sample) for db_sample in samples_query]
