import django
import os,json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mrnsdesign_api.settings")

django.setup()

from transcripthub.models import transcripthub_assembly, transcripthub_annotation, genome_seq
from mrnadesign_api import settings_local as local_settings
import pandas as pd
import glob
from Bio import SeqIO

cols = ['seqname', 'source', 'feature', 'start', 'end', 'score', 
    'strand', 'frame', 'attribute']
organ_list = ["AdiposeTissue", "AdiposeTissue_part2_Vagina", "Adrenal_Gland",
                "Bladder", "Blood_part1", "Blood_part2", "BloodVessel_part1", "BloodVessel_part2","Brain_part1", "Brain_part2", "Breast_Liver_FallopianTube", "CervixUteri", "Colon_part1", "Colon_part2", "Esophagus_part1", "Esophagus_part2", "Heart_part1", "Heart_part2", "Kidney", "Lung", "Muscle_part1", "Muscle_part2", "Nerve", "Ovary", "Pancreas", "Pituitary", "Prostate", "SalivaryGland", "Skin_part1", "Skin_part2","SmallIntestine", "Spleen", "Stomach", "Testis", "Thyroid_part1", "Thyroid_part2","Uterus",]

def add_data():

    # ======================================================================================================
    # data is too much and is a waste of resource, so just run for one record of one organ at this time
    # ======================================================================================================

    add_assembly_data()
    add_anno_data()

def add_assembly_data():

    for organ in organ_list:
        organ_assembly_path = local_settings.TRANSCRIPTHUB_ASSEMBLY / f'GTex_{organ}'
        record_path_list = list(organ_assembly_path.glob('*_stringTie.gtf')) # the standard glob.glob() function expects a string path.

        for record_path in record_path_list:

            record = os.path.basename(record_path).split('_')[0]
            assembly_df = pd.read_csv(local_settings.TRANSCRIPTHUB_ASSEMBLY / f'GTex_{organ}' / f'{record}_stringTie.gtf', 
                sep='\t',                   
                comment='#', # Skip comment lines
                header=None,
                names=cols)

            to_create = []
            for i, row in assembly_df.iterrows():
                record_dict = row.to_dict()
                record_dict['record'] = record
                record_dict['organism'] = organ
                to_create.append(transcripthub_assembly(**record_dict))

            transcripthub_assembly.objects.bulk_create(to_create, ignore_conflicts=True) # ignore_conflicts does not work 

            break
        break 

def add_anno_data():
    for organ in organ_list:
        organ_anno_path = local_settings.TRANSCRIPTHUB_ANNO / f'GTex_{organ}'
        gtf_path_list = list(organ_anno_path.glob('*.gtf'))
        
        for gtf_path in gtf_path_list:
            print(gtf_path)
            record = os.path.basename(gtf_path).split('.')[0]
            print(record)
            fa_path = local_settings.TRANSCRIPTHUB_ANNO / f'GTex_{organ}' / f'{record}_gffread_exons.fa'

            fa_dict = read_fasta(fa_path)
            fa_obj_dict = {}
            for k, v in fa_dict.items():
                g_obj, created = genome_seq.objects.get_or_create(seqname=k, sequence=v)
                fa_obj_dict[k] = g_obj

            anno_df = pd.read_csv(gtf_path, 
                sep='\t',                   
                comment='#', # Skip comment lines
                header=None,
                names=cols)

            to_create = []
            for i, row in anno_df.iterrows():
                record_dict = row.to_dict()
                if record_dict['score'] == ".":
                    record_dict['score'] = None
                record_dict['record'] = record
                record_dict['organism'] = organ
                record_dict['genome_sequence'] = fa_obj_dict.get(record_dict['seqname'], None)
                to_create.append(transcripthub_annotation(**record_dict))

            if to_create:
                transcripthub_annotation.objects.bulk_create(to_create, ignore_conflicts=True)
            break
        break

def read_fasta(fasta_path):
    return {record.id: str(record.seq) for record in SeqIO.parse(str(fasta_path), "fasta")}

if __name__ == "__main__":
    add_data()