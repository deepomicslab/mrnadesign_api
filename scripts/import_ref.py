import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")
django.setup()


def countgenessubcluster():
    from phage.models import phage
    newdict = {}
    with open("/home/platform/phage_db/phage_api/workspace/rawd_data/data_address.txt", 'r') as f:
        data_address_lines = f.readlines()
        for line in data_address_lines:

            newdict[line.split('\t')[0]] = line.split('\t')[1].strip('\n')
    phages = phage.objects.all()
    for ph in phages:
        ph.reference = newdict[ph.Acession_ID]
        ph.save()


countgenessubcluster()
