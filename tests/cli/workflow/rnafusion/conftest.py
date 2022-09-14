"""Fixtures for cli workflow rnafusion tests"""

import datetime as dt
import gzip
from pathlib import Path
from typing import List

import pytest
from cg.apps.hermes.hermes_api import HermesApi
from cg.apps.housekeeper.hk import HousekeeperAPI
from cg.constants import Pipeline
from cg.constants.constants import FileFormat
from cg.io.controller import WriteFile, WriteStream
from cg.meta.workflow.rnafusion import RnafusionAnalysisAPI
from cg.models.cg_config import CGConfig
from cg.store import Store
from tests.mocks.limsmock import MockLimsAPI
from tests.mocks.process_mock import ProcessMock
from tests.mocks.tb_mock import MockTB
from tests.store_helpers import StoreHelpers


@pytest.fixture(name="rnafusion_dir")
def balsamic_dir(tmpdir_factory, apps_dir: Path) -> str:
    """Return the path to the rnafusion apps dir"""
    balsamic_dir = tmpdir_factory.mktemp("rnafusion")
    return Path(rnafusion_dir).absolute().as_posix()


@pytest.fixture(name="rnafusion_case_id")
def fixture_rnafusion_case_id() -> str:
    return "rnafusion_case_id"


#
# @pytest.fixture(name="balsamic_housekeeper_dir")
# def balsamic_housekeeper_dir(tmpdir_factory, balsamic_dir: Path) -> Path:
#     """Return the path to the balsamic housekeeper bundle dir."""
#     return tmpdir_factory.mktemp("bundles")
#
#
# @pytest.fixture(name="balsamic_singularity_path")
# def balsamic_singularity_path(balsamic_dir: Path) -> str:
#     balsamic_singularity_path = Path(balsamic_dir, "singularity.sif")
#     balsamic_singularity_path.touch(exist_ok=True)
#     return balsamic_singularity_path.as_posix()
#
#
# @pytest.fixture(name="balsamic_reference_path")
# def balsamic_reference_path(balsamic_dir: Path) -> str:
#     balsamic_reference_path = Path(balsamic_dir, "reference.json")
#     balsamic_reference_path.touch(exist_ok=True)
#     return balsamic_reference_path.as_posix()
#
#
# @pytest.fixture(name="balsamic_pon_1_path")
# def balsamic_pon_1_path(balsamic_dir: Path) -> str:
#     balsamic_reference_path = Path(balsamic_dir, "balsamic_bed_1_case_PON_reference.cnn")
#     balsamic_reference_path.touch(exist_ok=True)
#     return balsamic_reference_path.as_posix()
#
#
# @pytest.fixture(name="balsamic_bed_1_path")
# def balsamic_bed_1_path(balsamic_dir: Path) -> str:
#     balsamic_bed_1_path = Path(balsamic_dir, "balsamic_bed_1.bed")
#     balsamic_bed_1_path.touch(exist_ok=True)
#     return balsamic_bed_1_path.as_posix()
#
#
# @pytest.fixture(name="balsamic_bed_2_path")
# def balsamic_bed_2_path(balsamic_dir: Path) -> str:
#     balsamic_bed_2_path = Path(balsamic_dir, "balsamic_bed_2.bed")
#     balsamic_bed_2_path.touch(exist_ok=True)
#     return balsamic_bed_2_path.as_posix()
#
#
# @pytest.fixture
# def fastq_file_l_1_r_1(balsamic_housekeeper_dir: Path) -> str:
#     fastq_filename = Path(
#         balsamic_housekeeper_dir, "XXXXXXXXX_000000_S000_L001_R1_001.fastq.gz"
#     ).as_posix()
#     with gzip.open(fastq_filename, "wb") as wh:
#         wh.write(b"@A00689:73:XXXXXXXXX:1:1101:4806:1047 1:N:0:TCCTGGAACA+ACAACCAGTA")
#     return fastq_filename
#
#
# @pytest.fixture
# def fastq_file_l_2_r_1(balsamic_housekeeper_dir: Path) -> str:
#     fastq_filename = Path(
#         balsamic_housekeeper_dir, "XXXXXXXXX_000000_S000_L002_R1_001.fastq.gz"
#     ).as_posix()
#     with gzip.open(fastq_filename, "wb") as wh:
#         wh.write(b"@A00689:73:XXXXXXXXX:2:1101:4806:1047 1:N:0:TCCTGGAACA+ACAACCAGTA")
#     return fastq_filename
#
#
# @pytest.fixture
# def fastq_file_l_3_r_1(balsamic_housekeeper_dir: Path) -> str:
#     fastq_filename = Path(
#         balsamic_housekeeper_dir, "XXXXXXXXX_000000_S000_L003_R1_001.fastq.gz"
#     ).as_posix()
#     with gzip.open(fastq_filename, "wb") as wh:
#         wh.write(b"@A00689:73:XXXXXXXXX:3:1101:4806:1047 1:N:0:TCCTGGAACA+ACAACCAGTA")
#     return fastq_filename
#
#
# @pytest.fixture
# def fastq_file_l_4_r_1(balsamic_housekeeper_dir: Path) -> str:
#     fastq_filename = Path(
#         balsamic_housekeeper_dir, "XXXXXXXXX_000000_S000_L004_R1_001.fastq.gz"
#     ).as_posix()
#     with gzip.open(fastq_filename, "wb") as wh:
#         wh.write(b"@A00689:73:XXXXXXXXX:4:1101:4806:1047 1:N:0:TCCTGGAACA+ACAACCAGTA")
#     return fastq_filename
#
#
# @pytest.fixture
# def fastq_file_l_1_r_2(balsamic_housekeeper_dir: Path) -> str:
#     fastq_filename = Path(
#         balsamic_housekeeper_dir, "XXXXXXXXX_000000_S000_L001_R2_001.fastq.gz"
#     ).as_posix()
#     with gzip.open(fastq_filename, "wb") as wh:
#         wh.write(b"@A00689:73:XXXXXXXXX:1:1101:4806:1047 2:N:0:TCCTGGAACA+ACAACCAGTA")
#     return fastq_filename
#
#
# @pytest.fixture
# def fastq_file_l_2_r_2(balsamic_housekeeper_dir: Path) -> str:
#     fastq_filename = Path(
#         balsamic_housekeeper_dir, "XXXXXXXXX_000000_S000_L002_R2_001.fastq.gz"
#     ).as_posix()
#     with gzip.open(fastq_filename, "wb") as wh:
#         wh.write(b"@A00689:73:XXXXXXXXX:2:1101:4806:1047 2:N:0:TCCTGGAACA+ACAACCAGTA")
#     return fastq_filename
#
#
# @pytest.fixture
# def fastq_file_l_3_r_2(balsamic_housekeeper_dir: Path) -> str:
#     fastq_filename = Path(
#         balsamic_housekeeper_dir, "XXXXXXXXX_000000_S000_L003_R2_001.fastq.gz"
#     ).as_posix()
#     with gzip.open(fastq_filename, "wb") as wh:
#         wh.write(b"@A00689:73:XXXXXXXXX:3:1101:4806:1047 2:N:0:TCCTGGAACA+ACAACCAGTA")
#     return fastq_filename
#
#
# @pytest.fixture
# def fastq_file_l_4_r_2(balsamic_housekeeper_dir: Path) -> str:
#     fastq_filename = Path(
#         balsamic_housekeeper_dir, "XXXXXXXXX_000000_S000_L004_R2_001.fastq.gz"
#     ).as_posix()
#     with gzip.open(fastq_filename, "wb") as wh:
#         wh.write(b"@A00689:73:XXXXXXXXX:4:1101:4806:1047 2:N:0:TCCTGGAACA+ACAACCAGTA")
#     return fastq_filename
#
#
# @pytest.fixture
# def balsamic_mock_fastq_files(
#     fastq_file_l_1_r_1: Path,
#     fastq_file_l_1_r_2: Path,
#     fastq_file_l_2_r_1: Path,
#     fastq_file_l_2_r_2: Path,
#     fastq_file_l_3_r_1: Path,
#     fastq_file_l_3_r_2: Path,
#     fastq_file_l_4_r_1: Path,
#     fastq_file_l_4_r_2: Path,
# ) -> list:
#     """Return list of all mock fastq files to commmit to mock housekeeper"""
#     return [
#         fastq_file_l_1_r_1,
#         fastq_file_l_1_r_2,
#         fastq_file_l_2_r_1,
#         fastq_file_l_2_r_2,
#         fastq_file_l_3_r_1,
#         fastq_file_l_3_r_2,
#         fastq_file_l_4_r_1,
#         fastq_file_l_4_r_2,
#     ]
#
#
# @pytest.fixture(scope="function", name="balsamic_housekeeper")
# def balsamic_housekeeper(housekeeper_api, helpers, balsamic_mock_fastq_files: list):
#     """Create populated housekeeper that holds files for all mock samples"""
#
#     samples = [
#         "sample_case_wgs_paired_tumor",
#         "sample_case_wgs_paired_normal",
#         "sample_case_tgs_paired_tumor",
#         "sample_case_tgs_paired_normal",
#         "sample_case_wgs_single_tumor",
#         "sample_case_tgs_single_tumor",
#         "sample_case_tgs_single_normal_error",
#         "sample_case_tgs_paired_tumor_error",
#         "sample_case_tgs_paired_tumor2_error",
#         "sample_case_tgs_paired_normal_error",
#         "mixed_sample_case_wgs_paired_tumor_error",
#         "mixed_sample_case_tgs_paired_normal_error",
#         "mixed_sample_case_mixed_bed_paired_tumor_error",
#         "mixed_sample_case_mixed_bed_paired_normal_error",
#         "mip_sample_case_wgs_single_tumor",
#         "sample_case_wgs_paired_two_normal_tumor_error",
#         "sample_case_wgs_paired_two_normal_normal1_error",
#         "sample_case_wgs_paired_two_normal_normal2_error",
#         "sample_case_wes_panel_error",
#         "sample_case_wes_tumor",
#     ]
#
#     for sample in samples:
#         bundle_data = {
#             "name": sample,
#             "created": dt.datetime.now(),
#             "version": "1.0",
#             "files": [
#                 {"path": f, "tags": ["fastq"], "archive": False} for f in balsamic_mock_fastq_files
#             ],
#         }
#         helpers.ensure_hk_bundle(store=housekeeper_api, bundle_data=bundle_data)
#     return housekeeper_api
#
#
# @pytest.fixture(name="balsamic_lims")
# def balsamic_lims(context_config: dict) -> MockLimsAPI:
#     """Create populated mock LIMS api to mimic all functionality of LIMS used by BALSAMIC"""
#
#     balsamic_lims = MockLimsAPI(context_config)
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_wgs_paired_tumor",
#         capture_kit=None,
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_wgs_paired_normal",
#         capture_kit=None,
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_tgs_paired_tumor",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_tgs_paired_normal",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_wgs_single_tumor",
#         capture_kit=None,
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_tgs_single_tumor",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_tgs_single_normal_error",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_tgs_paired_tumor_error",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_tgs_paired_tumor2_error",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_tgs_paired_normal_error",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="mixed_sample_case_wgs_paired_tumor_error",
#         capture_kit=None,
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="mixed_sample_case_tgs_paired_normal_error",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="mixed_sample_case_mixed_bed_paired_tumor_error",
#         capture_kit="BalsamicBed1",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="mixed_sample_case_mixed_bed_paired_normal_error",
#         capture_kit="BalsamicBed2",
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_wes_tumor",
#         capture_kit="BalsamicBed2",
#     )
#
#     balsamic_lims.add_capture_kit(
#         internal_id="mip_sample_case_wgs_single_tumor",
#         capture_kit=None,
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_wgs_paired_two_normal_tumor_error",
#         capture_kit=None,
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_wgs_paired_two_normal_normal1_error",
#         capture_kit=None,
#     )
#     balsamic_lims.add_capture_kit(
#         internal_id="sample_case_wgs_paired_two_normal_normal2_error",
#         capture_kit=None,
#     )
#
#     return balsamic_lims
#
#
@pytest.fixture(scope="function", name="rnafusion_context")
def fixture_rnafusion_context(
    cg_context: CGConfig,
    helpers: StoreHelpers,
    rnafusion_lims: MockLimsAPI,
    rnafusion_housekeeper: HousekeeperAPI,
    trailblazer_api: MockTB,
    hermes_api: HermesApi,
    cg_dir,
) -> CGConfig:
    """context to use in cli"""
    cg_context.housekeeper_api_ = rnafusion_housekeeper
    cg_context.lims_api_ = rnafusion_lims
    cg_context.trailblazer_api_ = trailblazer_api
    cg_context.meta_apis["analysis_api"] = RnafusionAnalysisAPI(config=cg_context)
    status_db: Store = cg_context.status_db

    sample_rnafusion = helpers.add_sample(
        status_db,
        internal_id="sample_rnafusion",
        reads=10,
        sequenced_at=dt.datetime.now(),
    )
    return cg_context


#
#
# @pytest.fixture
# def mock_config(balsamic_dir: Path, balsamic_case_id: str) -> None:
#     """Create dummy config file at specified path"""
#
#     config_data = {
#         "analysis": {
#             "case_id": f"{balsamic_case_id}",
#             "analysis_type": "paired",
#             "sequencing_type": "targeted",
#             "analysis_dir": f"{balsamic_dir}",
#             "fastq_path": f"{balsamic_dir}/{balsamic_case_id}/analysis/fastq/",
#             "script": f"{balsamic_dir}/{balsamic_case_id}/scripts/",
#             "log": f"{balsamic_dir}/{balsamic_case_id}/logs/",
#             "result": f"{balsamic_dir}/{balsamic_case_id}/analysis",
#             "benchmark": f"{balsamic_dir}/{balsamic_case_id}/benchmarks/",
#             "dag": f"{balsamic_dir}/{balsamic_case_id}/{balsamic_case_id}_BALSAMIC_4.4.0_graph.pdf",
#             "BALSAMIC_version": "4",
#             "config_creation_date": "2020-07-15 17:35",
#         }
#     }
#     Path.mkdir(Path(balsamic_dir, balsamic_case_id), parents=True, exist_ok=True)
#     WriteFile.write_file_from_content(
#         content=config_data,
#         file_format=FileFormat.JSON,
#         file_path=Path(balsamic_dir, balsamic_case_id, balsamic_case_id + ".json"),
#     )
#
#
# @pytest.fixture(name="deliverable_data")
# def fixture_deliverables_data(balsamic_dir: Path, balsamic_case_id: str) -> dict:
#     samples = [
#         "sample_case_wgs_single_tumor",
#     ]
#
#     return {
#         "files": [
#             {
#                 "path": f"{balsamic_dir}/{balsamic_case_id}/multiqc_report.html",
#                 "path_index": "",
#                 "step": "multiqc",
#                 "tag": ["qc"],
#                 "id": "T_WGS",
#                 "format": "html",
#                 "mandatory": True,
#             },
#             {
#                 "path": f"{balsamic_dir}/{balsamic_case_id}/concatenated_{samples[0]}_R_1.fp.fastq.gz",
#                 "path_index": "",
#                 "step": "fastp",
#                 "tag": [f"concatenated_{samples[0]}_R", "qc"],
#                 "id": f"concatenated_{samples[0]}_R",
#                 "format": "fastq.gz",
#                 "mandatory": True,
#             },
#             {
#                 "path": f"{balsamic_dir}/{balsamic_case_id}/CNV.somatic.{balsamic_case_id}.cnvkit.pass.vcf.gz.tbi",
#                 "path_index": "",
#                 "step": "vep_somatic",
#                 "format": "vcf.gz.tbi",
#                 "tag": [
#                     "CNV",
#                     balsamic_case_id,
#                     "cnvkit",
#                     "annotation",
#                     "somatic",
#                     "index",
#                 ],
#                 "id": balsamic_case_id,
#                 "mandatory": True,
#             },
#         ]
#     }
#
#
# @pytest.fixture
# def mock_deliverable(balsamic_dir: Path, deliverable_data: dict, balsamic_case_id: str) -> None:
#     """Create deliverable file with dummy data and files to deliver"""
#     Path.mkdir(
#         Path(balsamic_dir, balsamic_case_id, "analysis", "delivery_report"),
#         parents=True,
#         exist_ok=True,
#     )
#     for report_entry in deliverable_data["files"]:
#         Path(report_entry["path"]).touch(exist_ok=True)
#     WriteFile.write_file_from_content(
#         content=deliverable_data,
#         file_format=FileFormat.JSON,
#         file_path=Path(
#             balsamic_dir, balsamic_case_id, "analysis", "delivery_report", balsamic_case_id + ".hk"
#         ),
#     )
#
#
# @pytest.fixture(name="hermes_deliverables")
# def fixture_hermes_deliverables(deliverable_data: dict, balsamic_case_id: str) -> dict:
#     hermes_output: dict = {"pipeline": "balsamic", "bundle_id": balsamic_case_id, "files": []}
#     for file_info in deliverable_data["files"]:
#         tags: List[str] = []
#         if "html" in file_info["format"]:
#             tags.append("multiqc-html")
#         elif "fastq" in file_info["format"]:
#             tags.append("fastq")
#         elif "vcf" in file_info["format"]:
#             tags.extend(["vcf-snv-clinical", "cnvkit", "filtered"])
#         hermes_output["files"].append({"path": file_info["path"], "tags": tags, "mandatory": True})
#     return hermes_output
#
#
# @pytest.fixture(name="malformed_hermes_deliverables")
# def fixture_malformed_hermes_deliverables(hermes_deliverables: dict) -> dict:
#     malformed_deliverable = hermes_deliverables.copy()
#     malformed_deliverable.pop("pipeline")
#
#     return malformed_deliverable
#
#
# @pytest.fixture(name="balsamic_hermes_process")
# def fixture_balsamic_hermes_process(hermes_deliverables: dict, process: ProcessMock) -> ProcessMock:
#     """Return a process mock populated with some balsamic hermes output"""
#     process.set_stdout(
#         text=WriteStream.write_stream_from_content(
#             content=hermes_deliverables, file_format=FileFormat.JSON
#         )
#     )
#     return process
#
#
# @pytest.fixture
# def mock_analysis_finish(balsamic_dir: Path, balsamic_case_id: str) -> None:
#     """Create analysis_finish file for testing"""
#     Path.mkdir(Path(balsamic_dir, balsamic_case_id, "analysis"), parents=True, exist_ok=True)
#     Path(balsamic_dir, balsamic_case_id, "analysis", "analysis_finish").touch(exist_ok=True)
