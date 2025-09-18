from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.forms.models import model_to_dict
import sys
import pandas as pd

class Command(BaseCommand):
    help = 'Process internal database queries for tcrabpairing task'

    def add_arguments(self, parser):
        parser.add_argument('--user_input_path', type=str, help='Input file path')
        parser.add_argument('--output_result_path', type=str, help='Output file path')

    def process_col_name(self, chain, element):
        if chain == 'Alpha':
            if element == 'CDR3':
                return 'cdr3A'
            elif element == 'CDR3_nt':
                return 'cdr3_ntA'
            elif element == 'V Gene':
                return 'TRAV'
            elif element == 'J Gene':
                return 'TRAJ'
        else:  # Beta chain
            if element == 'CDR3':
                return 'cdr3B'
            elif element == 'CDR3_nt':
                return 'cdr3_ntB'
            elif element == 'V Gene':
                return 'TRBV'
            elif element == 'J Gene':
                return 'TRBJ'
        return None

    def handle(self, *args, **options):
        from tcrabpairing.models import tcrabpairing
        user_input_path = options.get('user_input_path')
        output_result_path = options.get('output_result_path')
        for i, items in pd.read_csv(user_input_path, sep='\t').iterrows():
            seq_id = items['seq_id']
            name = items['name']
            chain = items['chain']
            element = items['element']
            seq = items['seq']
            input_col = self.process_col_name(chain, element)
            if input_col is None:
                print(f"Invalid chain or element: {chain}, {element}", file=sys.stderr)
                continue
            filter_kwargs = {input_col: seq}
            result_qs = tcrabpairing.objects.filter(**filter_kwargs)
            data = [model_to_dict(obj) for obj in result_qs]
            result_df = pd.DataFrame(data, columns=[
                'id', 'source', 'barcode', 'Alpha', 'Beta', 'umisA', 'umisB', 'clonotype_freq',
                'TRAV', 'TRAJ', 'cdr3A', 'cdr3_ntA', 'readsA',
                'TRBV', 'TRBJ', 'cdr3B', 'cdr3_ntB', 'readsB', 'raw_clonotype_id'
            ])
            if result_df.empty:
                na_row = pd.DataFrame([['N/A'] * len(result_df.columns)], columns=result_df.columns)
                result_df = pd.concat([result_df, na_row], ignore_index=True)
            result_df.to_csv(f'{output_result_path}/{seq_id}_{name}_result.csv', index=False)
        print('Completed')
    