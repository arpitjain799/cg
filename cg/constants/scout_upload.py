from typing import Dict, Set

from cgmodels.cg.constants import StrEnum


class GenomeBuild(StrEnum):
    hg19: str = "37"
    hg38: str = "38"


MIP_CASE_TAGS = dict(
    snv_vcf={"vcf-snv-clinical"},
    snv_research_vcf={"vcf-snv-research"},
    sv_vcf={"vcf-sv-clinical"},
    sv_research_vcf={"vcf-sv-research"},
    vcf_str={"vcf-str"},
    smn_tsv={"smn-calling"},
    peddy_ped={"ped", "peddy"},
    peddy_sex={"sex-check", "peddy"},
    peddy_check={"ped-check", "peddy"},
    multiqc_report={"multiqc-html"},
    delivery_report={"delivery-report"},
    str_catalog={"expansionhunter", "variant-catalog"},
)

BALSAMIC_CASE_TAGS = dict(
    sv_vcf={"vcf-sv-clinical"},
    snv_vcf={"vcf-snv-clinical"},
    cnv_report={"cnv-report"},
    multiqc_report={"multiqc-html"},
    delivery_report={"delivery-report"},
)

BALSAMIC_UMI_CASE_TAGS = dict(
    sv_vcf={"vcf-umi-sv-clinical"},
    snv_vcf={"vcf-umi-snv-clinical"},
    multiqc_report={"multiqc-html"},
    delivery_report={"delivery-report"},
)

RNAFUSION_CASE_TAGS: Dict[str, Set[str]] = dict(
    multiqc_rna={"multiqc-html", "rna"},
    gene_fusion={"arriba-visualisation", "clinical"},
    gene_fusion_report_research={"arriba-visualisation", "research"},
    RNAfusion_report={"fusionreport", "clinical"},
    RNAfusion_report_research={"fusionreport", "research"},
    RNAfusion_inspector={"fusioninspector-html", "clinical"},
    RNAfusion_inspector_research={"fusioninspector-html", "research"},
)

MIP_SAMPLE_TAGS = dict(
    bam_file={"bam"},
    alignment_file={"cram"},
    vcf2cytosure={"vcf2cytosure"},
    mt_bam={"bam-mt"},
    chromograph_autozyg={"chromograph", "autozyg"},
    chromograph_coverage={"chromograph", "tcov"},
    chromograph_regions={"chromograph", "regions"},
    chromograph_sites={"chromograph", "sites"},
    reviewer_alignment={"expansionhunter", "bam"},
    reviewer_alignment_index={"expansionhunter", "bam-index"},
    reviewer_vcf={"expansionhunter", "vcf-str"},
    mitodel_file={"mitodel"},
)

BALSAMIC_SAMPLE_TAGS = dict(
    bam_file={"bam"},
    alignment_file={"cram"},
    vcf2cytosure={"vcf2cytosure"},
)

BALSAMIC_UMI_SAMPLE_TAGS = dict(
    bam_file={"umi-bam"},
    alignment_file={"umi-cram"},
)

RNAFUSION_SAMPLE_TAGS = dict()
