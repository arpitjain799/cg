"""Handler to find basic data objects"""
import datetime as dt
from typing import List, Optional

from sqlalchemy.orm import Query, Session

from cg.store.models import (
    Application,
    ApplicationVersion,
    Bed,
    BedVersion,
    Customer,
    Collaboration,
    Organism,
    Panel,
    User,
)
from cg.store.api.base import BaseHandler
from cg.store.filters.status_application_filters import apply_application_filter, ApplicationFilter
from cg.store.filters.status_application_version_filters import (
    apply_application_versions_filter,
    ApplicationVersionFilter,
)
from cg.store.filters.status_bed_filters import apply_bed_filter, BedFilter
from cg.store.filters.status_bed_version_filters import BedVersionFilter, apply_bed_version_filter
from cg.store.filters.status_collaboration_filters import (
    CollaborationFilter,
    apply_collaboration_filter,
)
from cg.store.filters.status_customer_filters import apply_customer_filter, CustomerFilter
from cg.store.filters.status_organism_filters import OrganismFilter, apply_organism_filter
from cg.store.filters.status_panel_filters import PanelFilter, apply_panel_filter
from cg.store.filters.status_user_filters import apply_user_filter, UserFilter


class FindBasicDataHandler(BaseHandler):
    """Contains methods to find basic data model instances."""

    def __init__(self, session: Session):
        super().__init__(session=session)

    def get_application_by_tag(self, tag: str) -> Application:
        """Return an application by tag."""
        return apply_application_filter(
            applications=self._get_query(table=Application),
            filter_functions=[ApplicationFilter.FILTER_BY_TAG],
            tag=tag,
        ).first()

    def get_applications_by_prep_category(self, prep_category: str) -> List[Application]:
        """Return applications by prep category."""
        return (
            apply_application_filter(
                applications=self._get_query(table=Application),
                filter_functions=[ApplicationFilter.FILTER_BY_PREP_CATEGORY],
                prep_category=prep_category,
            )
            .order_by(Application.prep_category, Application.tag)
            .all()
        )

    def get_applications_is_not_archived(self) -> List[Application]:
        """Return applications that are not archived."""
        return (
            apply_application_filter(
                applications=self._get_query(table=Application),
                filter_functions=[ApplicationFilter.FILTER_IS_NOT_ARCHIVED],
            )
            .order_by(Application.prep_category, Application.tag)
            .all()
        )

    def get_applications_by_prep_category_and_is_archived(
        self, prep_category: str
    ) -> List[Application]:
        """Return applications by prep category that are archived."""
        return (
            apply_application_filter(
                applications=self._get_query(table=Application),
                filter_functions=[
                    ApplicationFilter.FILTER_BY_PREP_CATEGORY,
                    ApplicationFilter.FILTER_IS_ARCHIVED,
                ],
                prep_category=prep_category,
            )
            .order_by(Application.prep_category, Application.tag)
            .all()
        )

    def get_applications(self) -> List[Application]:
        """Return all applications."""
        return (
            self._get_query(table=Application)
            .order_by(Application.prep_category, Application.tag)
            .all()
        )

    def get_application_version_by_application_entry_id(
        self, application_entry_id: int
    ) -> ApplicationVersion:
        """Return an application version by application entry id."""
        application_versions = self._get_query(table=ApplicationVersion)
        return apply_application_versions_filter(
            application_versions=application_versions,
            filter_functions=[ApplicationVersionFilter.FILTER_BY_APPLICATION_ENTRY_ID],
            application_entry_id=application_entry_id,
        ).first()

    def get_current_application_version_by_tag(self, tag: str) -> Optional[ApplicationVersion]:
        """Return the current application version for an application tag."""
        application = self.get_application_by_tag(tag=tag)
        if not application:
            return None
        return apply_application_versions_filter(
            filter_functions=[
                ApplicationVersionFilter.FILTER_BY_APPLICATION_ENTRY_ID,
                ApplicationVersionFilter.FILTER_BY_VALID_FROM_BEFORE,
                ApplicationVersionFilter.ORDER_BY_VALID_FROM_DESC,
            ],
            application_versions=self._get_query(table=ApplicationVersion),
            application_entry_id=application.id,
            valid_from=dt.datetime.now(),
        ).first()

    def get_application_versions(self) -> List[ApplicationVersion]:
        """Return all application versions."""
        return self._get_query(table=ApplicationVersion).all()

    def get_bed_version_by_short_name(self, bed_version_short_name: str) -> BedVersion:
        """Return bed version with short name."""
        return apply_bed_version_filter(
            bed_versions=self._get_query(table=BedVersion),
            bed_version_short_name=bed_version_short_name,
            filter_functions=[BedVersionFilter.FILTER_BY_SHORT_NAME],
        ).first()

    def get_bed_by_name(self, bed_name: str) -> Optional[Bed]:
        """Return bed by name."""
        return apply_bed_filter(
            beds=self._get_query(table=Bed),
            bed_name=bed_name,
            filter_functions=[BedFilter.FILTER_BY_NAME],
        ).first()

    def get_active_beds(self) -> Query:
        """Get all beds which are not archived."""
        bed_filter_functions: List[BedFilter] = [
            BedFilter.FILTER_NOT_ARCHIVED,
            BedFilter.ORDER_BY_NAME,
        ]
        return apply_bed_filter(
            beds=self._get_query(table=Bed), filter_functions=bed_filter_functions
        )

    def get_latest_bed_version(self, bed_name: str) -> Optional[BedVersion]:
        """Return the latest bed version for a bed by supplied name."""
        bed: Optional[Bed] = self.get_bed_by_name(bed_name=bed_name)
        return bed.versions[-1] if bed and bed.versions else None

    def get_customer_by_internal_id(self, customer_internal_id: str) -> Customer:
        """Return customer with customer id."""
        return apply_customer_filter(
            filter_functions=[CustomerFilter.FILTER_BY_INTERNAL_ID],
            customers=self._get_query(table=Customer),
            customer_internal_id=customer_internal_id,
        ).first()

    def get_collaboration_by_internal_id(self, internal_id: str) -> Collaboration:
        """Fetch a customer group by internal id from the store."""
        return apply_collaboration_filter(
            collaborations=self._get_query(table=Collaboration),
            filter_functions=[CollaborationFilter.FILTER_BY_INTERNAL_ID],
            internal_id=internal_id,
        ).first()

    def get_organism_by_internal_id(self, internal_id: str) -> Organism:
        """Find an organism by internal id."""
        return apply_organism_filter(
            organisms=self._get_query(table=Organism),
            filter_functions=[OrganismFilter.FILTER_BY_INTERNAL_ID],
            internal_id=internal_id,
        ).first()

    def get_all_organisms(self) -> List[Organism]:
        """Return all organisms ordered by organism internal id."""
        return self._get_query(table=Organism).order_by(Organism.internal_id)

    def get_customers(self) -> List[Customer]:
        """Return costumers."""
        return self._get_query(table=Customer).all()

    def get_panel_by_abbreviation(self, abbreviation: str) -> Panel:
        """Return a panel by abbreviation."""
        return apply_panel_filter(
            panels=self._get_query(table=Panel),
            filters=[PanelFilter.FILTER_BY_ABBREVIATION],
            abbreviation=abbreviation,
        ).first()

    def get_panels(self) -> List[Panel]:
        """Returns all panels."""
        return self._get_query(table=Panel).order_by(Panel.abbrev).all()

    def get_user_by_email(self, email: str) -> User:
        """Return a user by email from the database."""
        return apply_user_filter(
            users=self._get_query(table=User),
            email=email,
            filter_functions=[UserFilter.FILTER_BY_EMAIL],
        ).first()
