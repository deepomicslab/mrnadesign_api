import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()



def add_data():
    from phage.models import phage
    from phage_lifestyle.models import phage_lifestyle

    with open('/home/platform/phage_db/phage_api/workspace/rawd_data/lifestyle/Graphage_all_result.txt', 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip().split("\t")
        dp = phage.objects.get(Acession_ID=l[0])
        phage_lifestyle.objects.create(
            accesion_id=l[0], lifestyle=l[1], source=l[2],phage=dp)


if __name__ == "__main__":
    add_data()
