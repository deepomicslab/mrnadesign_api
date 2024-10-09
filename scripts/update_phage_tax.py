import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()



def add_data(taxdict):
    from phage.models import phage

    phages = phage.objects.all()
    for p in phages:
        p.taxonomy = taxdict[p.Acession_ID]
        p.save()

if __name__ == "__main__":
    taxdict={}
    with open('/home/platform/phage_db/phage_api/workspace/rawd_data/tax_v2.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split('\t')
            taxdict[line[0]] = line[1]

    add_data(taxdict)