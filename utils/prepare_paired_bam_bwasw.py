#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Xiaofei Zeng
# Email: xiaofei_zeng@whu.edu.cn
# Created Time: 2024-03-23 18:17


import argparse
import pysam
from itertools import combinations
from copy import copy

pysam.set_verbosity(0)


def parse_bam_for_falign(bam, mapq, percent_identity, alignment_length, threads):

    def parse_current_aln_list(current_aln_list, aln, fout):

        if len(current_aln_list) > 1:

            for n, (aln1, aln2) in enumerate(combinations(current_aln_list, 2)):

                aln1_copy, aln2_copy = copy(aln1), copy(aln2)

                mock_read_name = aln1_copy.query_name + '_read{}'.format(n)
                aln1_copy.query_name = aln2_copy.query_name = mock_read_name

                aln1_copy.flag += 65 + 2 * aln2.flag
                aln2_copy.flag += 129 + 2 * aln1.flag

                aln1_copy.next_reference_name = aln2.reference_name
                aln2_copy.next_reference_name = aln1.reference_name

                aln1_copy.next_reference_start = aln2.reference_start
                aln2_copy.next_reference_start = aln1.reference_start

                if mapq == 0 and aln1_copy.mapq == 0:
                    aln1_copy.mapq = 1
                if mapq == 0 and aln2_copy.mapq == 0:
                    aln2_copy.mapq = 1

                fout.write(aln1_copy)
                fout.write(aln2_copy)

        current_aln_list.clear()
        current_aln_list.append(aln)
        return aln.query_name


    current_aln_list = []
    current_read = None
    with pysam.AlignmentFile(bam, mode='rb', threads=threads, format_options=[b'filter=!flag.unmap']) as fin, \
            pysam.AlignmentFile('porec_paired.bam', mode='wb', threads=threads, template=fin) as fout:
        for aln in fin:
            # alignment filtering
            if aln.mapq < mapq:
                continue
            if (1 - aln.get_tag('NM') / aln.query_alignment_length) * 100 < percent_identity:
                continue
            if aln.query_alignment_length < alignment_length:
                continue

            if aln.query_name == current_read:
                current_aln_list.append(aln)
            else:
                current_read = parse_current_aln_list(current_aln_list, aln, fout)
        parse_current_aln_list(current_aln_list, aln, fout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bam', help='the BAM file generated by falign')
    parser.add_argument('--mapq', type=int, default=1, help='MAPQ cutoff, read pairs with both MAPQ >= this value will be kept, default: %(default)s')
    parser.add_argument('--percent_identity', type=float, default=90, help='percent identity cutoff, read pairs with both percent identity >= this value will be kept, default: %(default)s')
    parser.add_argument('--alignment_length', type=int, default=150, help='alignment length cutoff, read pairs with both alignment length >= this value will be kept, default: %(default)s')
    parser.add_argument('--threads', type=int, default=8, help='threads for parsing BAM file, default: %(default)s')
    args = parser.parse_args()

    parse_bam_for_falign(args.bam, args.mapq, args.percent_identity, args.alignment_length, args.threads)


if __name__ == '__main__':
    main()
