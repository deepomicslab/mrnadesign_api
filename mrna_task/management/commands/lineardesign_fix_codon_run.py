from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.forms.models import model_to_dict
import sys
import os
import pandas as pd
from Bio import SeqIO

dependency_path = os.path.dirname(os.path.join(os.path.dirname(__file__), 'LinearDesignFixCodon'))
if dependency_path not in sys.path:
    sys.path.insert(0, dependency_path)

from LinearDesignFixCodon import linear_design_fix_codon, base, settings

class Command(BaseCommand):
    help = 'Process internal database queries for tcrabpairing task'

    def add_arguments(self, parser):
        parser.add_argument('--seq_fasta_path', type=str, help='Input fasta path')
        parser.add_argument('--fix_codon_config', type=str, help='Codon fix config')
        parser.add_argument('--lambda', type=str, help='Param lambda')
        parser.add_argument('--codonusage', type=str, help='Param codon usage')
        parser.add_argument('--output_result_path', type=str, help='Output file path')

    def get_first_sequence(self, filename):
        for record in SeqIO.parse(filename, "fasta"):
            return record  # Return immediately after first sequence
        return None  # Return None if file is empty

    def handle(self, *args, **options):
        seq_fasta_path = options.get('seq_fasta_path')
        fix_codon_config = options.get('fix_codon_config')
        lambda_ = options.get('lambda') # leave for future extension
        codonusage = options.get('codonusage') # leave for future extension
        output_result_path = options.get('output_result_path')

        aa_seq = self.get_first_sequence(seq_fasta_path) # "MSYYLNYYGGLGYGYDCKYSY*"
        params = base.load_energy_params(settings.get_abs_home() / 'original_parameters') # "./original_parameters"
        result = linear_design_fix_codon.linearDesign_one_seq(aa_seq.seq, params, codon_constraints_csv = fix_codon_config) # "./overrides.csv"
        with open(output_result_path + '/result.txt', 'w') as fin:
            fin.write('>' + aa_seq.name + '\n')
            fin.write(result)

# 对 siqi 的脚本做以下改动：
    # return result
    # 加 __init__.py
    # 把 base 里面的 import codon 改成 import .codon
    # 同上 from . import base
    # 其他同理。否则会找不到或者冲突
    # 把所有 ./original_parameters 换成绝对路径