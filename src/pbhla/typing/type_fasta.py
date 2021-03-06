#! /usr/bin/env python

import os, logging

from pbhla.external.utils import full_align_best_reference, align_best_reference
from pbhla.external.align_by_identity import align_by_identity
from pbhla.fasta.orient_fasta import orient_fasta
from pbhla.annotation.extract_alleles import extract_alleles
from pbhla.annotation.extract_cDNA import extract_cDNA
from pbhla.annotation.summarize_typing import summarize_typing
from pbhla.annotation.create_chimeras import create_chimeras
from pbhla.io.extract_best_reads import extract_best_reads
from pbhla.fasta.utils import combine_fasta
from pbhla.annotation.summarize_alleles import summarize_alleles

log = logging.getLogger()

def type_fasta( input_fofn, input_fasta, exon_fofn, genomic_reference, cDNA_reference ):
    """
    Pick the top N Amplicon Analysis consensus seqs from a Fasta by Nreads
    """
    # First we align the sequences to the reference and annotate typing
    raw_alignment = align_best_reference( input_fasta, genomic_reference )
    reoriented = orient_fasta( input_fasta, alignment_file=raw_alignment )
    selected = extract_alleles( reoriented, alignment_file=raw_alignment )
    gDNA_alignment = full_align_best_reference( selected, genomic_reference )
    cDNA_file = extract_cDNA( selected, exon_fofn, alignment_file=gDNA_alignment )
    cDNA_alignment = align_by_identity( cDNA_file, cDNA_reference )
    summarize_typing( gDNA_alignment, cDNA_alignment )
    # Next we generate some mock chimera sequences
    chimera_file = create_chimeras( selected, alignment_file=gDNA_alignment )
    basename = '.'.join( chimera_file.split('.')[:-2] )
    combined_file = '%s.combined.fasta' % basename
    combine_fasta( [input_fasta, chimera_file], combined_file )
    # Finally we use a competetive alignment of best-reads to summarize the allelic breakdown
    dirname = os.path.dirname( input_fasta )
    best_reads = os.path.join( dirname, 'reads_of_insert.fasta' )
    extract_best_reads( input_fofn, best_reads )
    best_alignment = align_best_reference( best_reads, combined_file )
    summarize_alleles( best_alignment, raw_alignment, selected )

if __name__ == '__main__':
    import sys
    logging.basicConfig( level=logging.INFO )

    input_fofn = sys.argv[1]
    input_fasta = sys.argv[2]
    exon_fofn = sys.argv[3]
    genomic_reference = sys.argv[4]
    cDNA_reference = sys.argv[5]
    
    type_fasta( input_fofn, input_fasta,  exon_fofn, genomic_reference, cDNA_reference )
