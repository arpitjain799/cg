from cgmodels.cg.constants import Pipeline, StrEnum


class OrderType(StrEnum):
    BALSAMIC: str = str(Pipeline.BALSAMIC)
    FASTQ: str = str(Pipeline.FASTQ)
    FLUFFY: str = str(Pipeline.FLUFFY)
    METAGENOME: str = "metagenome"
    MICROSALT: str = str(Pipeline.MICROSALT)
    MIP_DNA: str = str(Pipeline.MIP_DNA)
    MIP_RNA: str = str(Pipeline.MIP_RNA)
    RML: str = "rml"
    SARS_COV_2: str = str(Pipeline.SARS_COV_2)