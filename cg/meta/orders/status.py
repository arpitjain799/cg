"""Ordering module"""
import datetime as dt
from typing import Dict, List, Optional

from cg.constants import DataDelivery, Pipeline
from cg.exc import OrderError
from cg.meta.orders.pools import get_pools
from cg.meta.orders.rml_order_form import (
    Orderform,
    OrderSample,
    Pool,
    RMLOrderform,
    StatusData,
    StatusSample,
)
from cg.store import models


class StatusHandler:
    """Handles ordering data for the statusDB"""

    def __init__(self):
        self.status = None

    @staticmethod
    def group_cases(samples: List[dict]) -> dict:
        """Group samples in cases."""
        cases = {}
        for sample in samples:
            case_id = sample["family_name"]
            if case_id not in cases:
                cases[case_id] = []
            cases[case_id].append(sample)
        return cases

    @staticmethod
    def get_status_data(data: dict) -> Orderform:
        return Orderform(**data)

    @staticmethod
    def pools_to_status(data: dict) -> Orderform:
        """Convert input to pools."""
        orderform: Orderform = StatusHandler.get_status_data(data)
        orderform.pools = get_pools(orderform)

        return orderform

    @staticmethod
    def samples_to_status(data: dict) -> dict:
        """Convert order input to status for fastq-only/metagenome orders."""
        status_data = {
            "customer": data["customer"],
            "order": data["name"],
            "samples": [
                {
                    "application": sample["application"],
                    "comment": sample.get("comment"),
                    "data_analysis": sample["data_analysis"],
                    "data_delivery": sample.get("data_delivery"),
                    "internal_id": sample.get("internal_id"),
                    "name": sample["name"],
                    "priority": sample["priority"],
                    "sex": sample.get("sex"),
                    "status": sample.get("status"),
                    "tumour": sample.get("tumour") or False,
                }
                for sample in data["samples"]
            ],
        }
        return status_data

    @staticmethod
    def microbial_samples_to_status(data: dict) -> dict:
        """Convert order input for microbial samples."""

        status_data = {
            "customer": data["customer"],
            "order": data["name"],
            "comment": data.get("comment"),
            "data_analysis": data["samples"][0]["data_analysis"],
            "data_delivery": data["samples"][0]["data_delivery"],
            "samples": [
                {
                    "application": sample_data["application"],
                    "comment": sample_data.get("comment"),
                    "data_delivery": sample_data.get("data_delivery"),
                    "internal_id": sample_data.get("internal_id"),
                    "name": sample_data["name"],
                    "organism_id": sample_data["organism"],
                    "priority": sample_data["priority"],
                    "reference_genome": sample_data["reference_genome"],
                }
                for sample_data in data["samples"]
            ],
        }
        return status_data

    @classmethod
    def cases_to_status(cls, data: dict) -> dict:
        """Convert order input to status interface input."""
        status_data = {"customer": data["customer"], "order": data["name"], "families": []}
        cases = cls.group_cases(data["samples"])

        for case_name, case_samples in cases.items():
            priority = cls.get_single_value(case_name, case_samples, "priority", "standard")
            data_analysis = cls.get_single_value(case_name, case_samples, "data_analysis")
            data_delivery = cls.get_single_value(case_name, case_samples, "data_delivery")

            panels = set(panel for sample in case_samples for panel in sample.get("panels", set()))
            case = {
                # Set from first sample until order portal sets this on case level
                "data_analysis": data_analysis,
                "data_delivery": data_delivery,
                "name": case_name,
                "priority": priority,
                "panels": list(panels),
                "samples": [
                    {
                        "application": sample["application"],
                        "capture_kit": sample.get("capture_kit"),
                        "cohorts": list(sample.get("cohorts")),
                        "comment": sample.get("comment"),
                        "father": sample.get("father"),
                        "from_sample": sample.get("from_sample"),
                        "internal_id": sample.get("internal_id"),
                        "mother": sample.get("mother"),
                        "name": sample["name"],
                        "phenotype_terms": list(sample.get("phenotype_terms")),
                        "sex": sample["sex"],
                        "status": sample.get("status"),
                        "synopsis": list(sample.get("synopsis")),
                        "time_point": sample.get("time_point"),
                        "tumour": sample.get("tumour", False),
                    }
                    for sample in case_samples
                ],
            }

            status_data["families"].append(case)
        return status_data

    @classmethod
    def get_single_value(cls, case_name, case_samples, value_key, value_default=None):
        values = {sample.get(value_key, value_default) for sample in case_samples}
        if len(values) > 1:
            raise ValueError(f"different sample {value_key} values: {case_name} - {values}")
        return values.pop()

    def store_cases(
        self, customer: str, order: str, ordered: dt.datetime, ticket: int, cases: List[dict]
    ) -> List[models.Family]:
        """Store cases and samples in the status database."""

        customer_obj: Optional[models.Customer] = self.status.customer(customer)
        if customer_obj is None:
            raise OrderError(f"unknown customer: {customer}")
        new_cases: List[models.Family] = []
        for case in cases:
            case_obj: Optional[models.Family] = self.status.find_family(customer_obj, case["name"])
            if case_obj:
                case_obj.panels = case["panels"]
            else:
                case_obj = self.status.add_case(
                    data_analysis=Pipeline(case["data_analysis"]),
                    data_delivery=DataDelivery(case["data_delivery"]),
                    name=case["name"],
                    panels=case["panels"],
                    priority=case["priority"],
                )
                case_obj.customer = customer_obj
                new_cases.append(case_obj)

            family_samples = {}
            for sample in case["samples"]:
                sample_obj: Optional[models.Sample] = self.status.sample(sample["internal_id"])
                if sample_obj:
                    family_samples[sample["name"]] = sample_obj
                    continue

                new_sample: models.Sample = self.status.add_sample(
                    capture_kit=sample["capture_kit"],
                    cohorts=sample["cohorts"],
                    comment=sample["comment"],
                    from_sample=sample["from_sample"],
                    internal_id=sample["internal_id"],
                    name=sample["name"],
                    order=order,
                    ordered=ordered,
                    phenotype_terms=sample["phenotype_terms"],
                    priority=case["priority"],
                    sex=sample["sex"],
                    synopsis=sample["synopsis"],
                    ticket=ticket,
                    time_point=sample["time_point"],
                    tumour=sample["tumour"],
                )
                new_sample.customer = customer_obj
                with self.status.session.no_autoflush:
                    application_tag: str = sample["application"]
                    new_sample.application_version: Optional[
                        models.ApplicationVersion
                    ] = self.status.current_application_version(application_tag)
                if new_sample.application_version is None:
                    raise OrderError(f"Invalid application: {sample['application']}")

                family_samples[new_sample.name] = new_sample
                self.status.add(new_sample)
                new_delivery = self.status.add_delivery(destination="caesar", sample=new_sample)
                self.status.add(new_delivery)

            # Create links
            for sample in case["samples"]:
                mother_obj = family_samples[sample["mother"]] if sample.get("mother") else None
                father_obj = family_samples[sample["father"]] if sample.get("father") else None
                with self.status.session.no_autoflush:
                    link_obj = self.status.link(case_obj.internal_id, sample["internal_id"])
                if link_obj:
                    link_obj.status = sample["status"] or link_obj.status
                    link_obj.mother = mother_obj or link_obj.mother
                    link_obj.father = father_obj or link_obj.father
                else:
                    new_link = self.status.relate_sample(
                        family=case_obj,
                        sample=family_samples[sample["name"]],
                        status=sample["status"],
                        mother=mother_obj,
                        father=father_obj,
                    )
                    self.status.add(new_link)
            self.status.add_commit(new_cases)
        return new_cases

    def store_samples(
        self, customer: str, order: str, ordered: dt.datetime, ticket: int, samples: List[dict]
    ) -> List[models.Sample]:
        """Store samples in the status database."""
        customer_obj: Optional[models.Customer] = self.status.customer(customer)
        if customer_obj is None:
            raise OrderError(f"unknown customer: {customer}")
        new_samples: List[models.Sample] = []

        with self.status.session.no_autoflush:
            for sample in samples:
                new_sample: models.Sample = self.status.add_sample(
                    comment=sample["comment"],
                    internal_id=sample["internal_id"],
                    name=sample["name"],
                    order=order,
                    ordered=ordered,
                    priority=sample["priority"],
                    sex=sample["sex"] or "unknown",
                    ticket=ticket,
                    tumour=sample["tumour"],
                )
                new_sample.customer = customer_obj
                application_tag: str = sample["application"]
                application_version: Optional[
                    models.ApplicationVersion
                ] = self.status.current_application_version(application_tag)
                if application_version is None:
                    raise OrderError(f"Invalid application: {sample['application']}")
                new_sample.application_version = application_version
                new_samples.append(new_sample)

                new_case: models.Family = self.status.add_case(
                    data_analysis=Pipeline(sample["data_analysis"]),
                    data_delivery=DataDelivery(sample["data_delivery"]),
                    name=sample["name"],
                    panels=None,
                    priority=sample["priority"],
                )
                new_case.customer = customer_obj
                self.status.add(new_case)

                new_relationship = self.status.relate_sample(
                    family=new_case, sample=new_sample, status=sample["status"] or "unknown"
                )
                self.status.add(new_relationship)

        self.status.add_commit(new_samples)
        return new_samples

    def store_fastq_samples(
        self, customer: str, order: str, ordered: dt.datetime, ticket: int, samples: List[dict]
    ) -> List[models.Sample]:
        """Store fastq samples in the status database including family connection and delivery"""
        production_customer: models.Customer = self.status.customer("cust000")
        customer_obj: Optional[models.Customer] = self.status.customer(customer)
        if customer_obj is None:
            raise OrderError(f"unknown customer: {customer}")
        new_samples: List[models.Sample] = []

        with self.status.session.no_autoflush:
            for sample in samples:
                new_sample = self.status.add_sample(
                    name=sample["name"],
                    internal_id=sample["internal_id"],
                    sex=sample["sex"] or "unknown",
                    order=order,
                    ordered=ordered,
                    ticket=ticket,
                    priority=sample["priority"],
                    comment=sample["comment"],
                    tumour=sample["tumour"],
                )
                new_sample.customer = customer_obj
                application_tag: str = sample["application"]
                application_version: Optional[
                    models.ApplicationVersion
                ] = self.status.current_application_version(application_tag)
                if application_version is None:
                    raise OrderError(f"Invalid application: {sample['application']}")
                new_sample.application_version = application_version
                new_samples.append(new_sample)
                new_case = self.status.add_case(
                    data_analysis=Pipeline(sample["data_analysis"]),
                    data_delivery=DataDelivery(sample["data_delivery"]),
                    name=sample["name"],
                    panels=["OMIM-AUTO"],
                    priority="research",
                )
                new_case.customer = production_customer
                self.status.add(new_case)
                new_relationship = self.status.relate_sample(
                    family=new_case, sample=new_sample, status=sample["status"] or "unknown"
                )
                self.status.add(new_relationship)
                new_delivery: models.Delivery = self.status.add_delivery(
                    destination="caesar", sample=new_sample
                )
                self.status.add(new_delivery)

        self.status.add_commit(new_samples)
        return new_samples

    def store_microbial_samples(
        self,
        comment: str,
        customer: str,
        data_analysis: Pipeline,
        data_delivery: DataDelivery,
        order: str,
        ordered: dt.datetime,
        samples: List[dict],
        ticket: int,
    ) -> [models.Sample]:
        """Store microbial samples in the status database."""

        sample_objs = []

        customer_obj = self.status.customer(customer)
        if customer_obj is None:
            raise OrderError(f"unknown customer: {customer}")

        new_samples = []

        with self.status.session.no_autoflush:

            for sample_data in samples:
                case_obj = self.status.find_family(customer=customer_obj, name=ticket)

                if not case_obj:
                    case_obj = self.status.add_case(
                        data_analysis=data_analysis,
                        data_delivery=data_delivery,
                        name=ticket,
                        panels=None,
                    )
                    case_obj.customer = customer_obj
                    self.status.add_commit(case_obj)

                application_tag = sample_data["application"]
                application_version = self.status.current_application_version(application_tag)
                if application_version is None:
                    raise OrderError(f"Invalid application: {sample_data['application']}")

                organism = self.status.organism(sample_data["organism_id"])

                if not organism:
                    organism = self.status.add_organism(
                        internal_id=sample_data["organism_id"],
                        name=sample_data["organism_id"],
                        reference_genome=sample_data["reference_genome"],
                    )
                    self.status.add_commit(organism)

                if comment:
                    case_obj.comment = f"Order comment: {comment}"

                new_sample = self.status.add_sample(
                    application_version=application_version,
                    comment=sample_data["comment"],
                    customer=customer_obj,
                    data_delivery=sample_data["data_delivery"],
                    internal_id=sample_data["internal_id"],
                    name=sample_data["name"],
                    order=order,
                    ordered=ordered,
                    organism=organism,
                    priority=sample_data["priority"],
                    reference_genome=sample_data["reference_genome"],
                    sex="unknown",
                    ticket=ticket,
                )

                priority = new_sample.priority

                sample_objs.append(new_sample)
                self.status.relate_sample(family=case_obj, sample=new_sample, status="unknown")
                new_samples.append(new_sample)

            case_obj.priority = priority
            self.status.add_commit(new_samples)
        return sample_objs

    def store_rml(
        self, customer: str, order: str, ordered: dt.datetime, ticket: int, pools: List[Pool]
    ) -> List[models.Pool]:
        """Store pools in the status database."""
        customer_obj: Optional[models.Customer] = self.status.customer(customer)
        if customer_obj is None:
            raise OrderError(f"unknown customer: {customer}")
        new_pools: List[models.Pool] = []
        new_samples: List[models.Sample] = []
        pool: Pool
        for pool in pools:
            with self.status.session.no_autoflush:
                application_version = self.status.current_application_version(pool.application)
                if application_version is None:
                    raise OrderError(f"Invalid application: {pool.application}")

            case_name = f"{ticket}-{pool.name}"
            case_obj: Optional[models.Family] = self.status.find_family(
                customer=customer_obj, name=case_name
            )

            if not case_obj:
                case_obj: models.Family = self.status.add_case(
                    data_analysis=Pipeline(pool.data_analysis),
                    data_delivery=DataDelivery(pool.data_delivery),
                    name=case_name,
                    panels=None,
                )
                case_obj.customer = customer_obj
                self.status.add_commit(case_obj)

            new_pool: models.Pool = self.status.add_pool(
                customer=customer_obj,
                name=pool.name,
                order=order,
                ordered=ordered,
                ticket=ticket,
                application_version=application_version,
            )
            sample: StatusSample
            for sample in pool.samples:
                new_sample: models.Sample = self.status.add_sample(
                    application_version=application_version,
                    comment=sample.comment,
                    customer=customer_obj,
                    internal_id=sample.internal_id,
                    name=sample.name,
                    order=order,
                    ordered=ordered,
                    priority=sample.priority,
                    sex="unknown",
                    ticket=ticket,
                )
                new_samples.append(new_sample)
                self.status.relate_sample(family=case_obj, sample=new_sample, status="unknown")
            new_delivery: models.Delivery = self.status.add_delivery(
                destination="caesar", pool=new_pool
            )
            self.status.add(new_delivery)
            new_pools.append(new_pool)
        self.status.add_commit(new_pools)
        return new_pools
