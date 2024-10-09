import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
# trna_id, trnatype, start, end, strand,length,permutation,seq,phage_accid


def add_data():
    from phage.models import phage
    from phage_trna.models import phage_trna

    with open('/home/platform/phage_db/phage_api/workspace/data_revision/tRNA/trna2.tsv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split("\t")
        dp = phage.objects.get(Acession_ID=l[9])

        phage_trna.objects.create(
            trna_id=l[0], trnatype=l[2], start=l[3], end=l[4], strand=l[5], length=l[6], permutation=l[7], seq=l[8], phage_accid=l[9], phage=dp)


if __name__ == "__main__":
    add_data()