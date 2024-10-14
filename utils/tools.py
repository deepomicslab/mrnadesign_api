from Bio import SeqIO
# from phage.models import phage
# from phage.serializers import phageSerializer

def is_fasta(fatsapath):
    try:
        for record in SeqIO.parse(fatsapath, 'fasta'):
            pass
        return True
    except:
        return False

def sequence_count(fatsapath):
    seq_records=SeqIO.parse(fatsapath, "fasta")
    return len(list(seq_records))



def uploadphagefastapreprocess(fatsapath):
    """preprocessed file to standard fasta format"""
    seq_dic = {}
    for seq_record in SeqIO.parse(fatsapath, "fasta"):
        seq_dic[seq_record.id] = str(seq_record.seq)

    f_out = open(fatsapath, "w")
    for seq_id in seq_dic:
        f_out.write(">" + seq_id + "\n")
        seq = seq_dic[seq_id]
        while len(seq) > 70:
            f_out.write(seq[:70] + "\n")
            seq = seq[70:]
        f_out.write(seq + "\n")
    f_out.close()


# def fixIdLong(fatsapath):
#     seq_dic = {}
#     for seq_record in SeqIO.parse(fatsapath, "fasta"):
#         seq_dic[seq_record.id] = str(seq_record.seq)
#     f_out = open(fatsapath, "w")
#     for seq_id in seq_dic:
#         if len(seq_id) > 47:
#             seqid = seq_id[-47:]
#         else:
#             seqid = seq_id
#         f_out.write(">" + seqid + "\n")
#         f_out.write(seq_dic[seq_id] + "\n")
#     f_out.close()


# def searchphagefasta(phageids, path):
#     phages = phage.objects.filter(Acession_ID__in=phageids)
#     phagedatas = phageSerializer(phages, many=True).data
#     with open(path, 'w') as f:
#         for phagedata in phagedatas:
#             with open(phagedata['fastapath'], 'r') as f1:
#                 f.write(f1.read()+'\n')