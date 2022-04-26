"""Constants related to all things sequencing"""
from enum import Enum

from cgmodels.cg.constants import StrEnum

sequencer_types = {
    "D00134": "hiseqga",
    "D00410": "hiseqga",
    "D00415": "hiseqga",
    "D00450": "hiseqga",
    "D00456": "hiseqga",
    "D00483": "hiseqga",
    "M03284": "hiseqga",
    "SN1025": "hiseqga",
    "SN7001298": "hiseqga",
    "SN7001301": "hiseqga",
    "ST-E00198": "hiseqx",
    "ST-E00201": "hiseqx",
    "ST-E00214": "hiseqx",
    "ST-E00266": "hiseqx",
    "ST-E00269": "hiseqx",
    "A00187": "novaseq",
    "A00621": "novaseq",
    "A00689": "novaseq",
}


class SequencingMethod(str, Enum):
    ILLUMINA = "illumina"


class PreparationCategory(str, Enum):
    SARS2_COV = "cov"
    MICRO = "mic"
    READY_MADE_LIBRARY = "rml"
    TARGETED_GENOME_SEQUENCING = "tgs"
    WHOLE_EXOME_SEQUENCING = "wes"
    WHOLE_GENOME_SEQUENCING = "wgs"
    WHOLE_TRANSCRIPTOME_SEQUENCING = "wts"


class Sequencers(StrEnum):
    NOVASEQ: str = "novaseq"
    HISEQGA: str = "hiseqga"
    HISEQX: str = "hiseqx"
