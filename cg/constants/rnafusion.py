"""RNAfusion related constants."""


from cg.constants.nextflow import NFX_SAMPLESHEET_HEADERS

RNAFUSION_STRANDEDNESS_DEFAULT = "reverse"
RNAFUSION_ACCEPTED_STRANDEDNESS = ["forward", "reverse", "unstranded"]
RNAFUSION_STRANDEDNESS_HEADER = "strandedness"
RNAFUSION_SAMPLESHEET_HEADERS = NFX_SAMPLESHEET_HEADERS + [RNAFUSION_STRANDEDNESS_HEADER]