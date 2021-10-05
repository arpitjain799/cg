"""Constants for cg"""
from cgmodels.cg.constants import Pipeline, StrEnum

CONTAINER_OPTIONS = ("Tube", "96 well plate", "No container")

CAPTUREKIT_OPTIONS = (
    "Agilent Sureselect CRE",
    "Agilent Sureselect V5",
    "SureSelect Focused Exome",
    "Twist_Target_hg19.bed",
    "other",
)

CAPTUREKIT_CANCER_OPTIONS = (
    "GIcfDNA",
    "GMCKsolid",
    "GMSmyeloid",
    "LymphoMATIC",
    "other (specify in comment field)",
)

COMBOS = {
    "DSD": ("DSD", "HYP", "SEXDIF", "SEXDET"),
    "CM": ("CNM", "CM"),
    "Horsel": ("Horsel", "141217", "141201"),
}

CONTROL_OPTIONS = ("", "negative", "positive")

COLLABORATORS = ("cust000", "cust002", "cust003", "cust004", "cust042")

DEFAULT_CAPTURE_KIT = "twistexomerefseq_9.1_hg19_design.bed"

CASE_ACTIONS = ("analyze", "running", "hold")

FLOWCELL_STATUS = ("ondisk", "removed", "requested", "processing", "retrieved")


class DataDelivery(StrEnum):
    ANALYSIS_BAM_FILES: str = "analysis-bam"
    ANALYSIS_FILES: str = "analysis"
    FASTQ: str = "fastq"
    FASTQ_QC: str = "fastq_qc"
    FASTQ_QC_ANALYSIS_CRAM: str = "fastq_qc-analysis-cram"
    FASTQ_QC_ANALYSIS_CRAM_SCOUT: str = "fastq_qc-analysis-cram-scout"
    NIPT_VIEWER: str = "nipt-viewer"
    SCOUT: str = "scout"


PREP_CATEGORIES = ("cov", "mic", "rml", "tgs", "wes", "wgs", "wts")

SEX_OPTIONS = ("male", "female", "unknown")

STATUS_OPTIONS = ("affected", "unaffected", "unknown")
ANALYSIS_TYPES = ["tumor_wgs", "tumor_normal_wgs", "tumor_panel", "tumor_normal_panel"]
