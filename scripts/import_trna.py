import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
# trna_id, trnatype, start, end, strand,length,permutation,seq,phage_accid


def add_data():
    from phage.models import phage
    from phage_trna.models import phage_trna

    with open('/home/platform/phage_db/phage_api/workspace/csv_data/tRNA.csv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split("\t")
        dp = phage.objects.get(Acession_ID=l[8])

        phage_trna.objects.create(
            trna_id=l[0], trnatype=l[1], start=l[2], end=l[3], strand=l[4], length=l[5], permutation=l[6], seq=l[7], phage_accid=l[8], phage=dp)


if __name__ == "__main__":
    add_data()
