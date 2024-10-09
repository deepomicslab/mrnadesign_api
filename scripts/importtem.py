import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()

# # Phage_ID	Terminator	Start	Stop	Sense	Loc	Confidence
# Phage_id = models.CharField(max_length=500, blank=True, null=True)
# Terminator_Id = models.CharField(max_length=200, blank=True, null=True)
# Start = models.CharField(max_length=200, blank=True, null=True)
# Stop = models.CharField(max_length=200, blank=True, null=True)
# Sense = models.CharField(max_length=200, blank=True, null=True)
# Loc = models.CharField(max_length=200, blank=True, null=True)
# Confidence = models.CharField(max_length=200, blank=True, null=True)


def add_data():
    from phage_protein.models import phage_terminators

    with open('/home/platform/phage_db/phage_api/workspace/csv_data/terminator/all.tsv', 'r') as f:
        lines = f.readlines()

    for line in lines:
        if 'Phage_ID	Terminator' in line:
            continue
        else:
            l = line.strip().split("\t")
            phage_terminators.objects.create(
                Phage_id=l[0], Terminator_Id=l[1], Start=l[2], Stop=l[3], Sense=l[4], Loc=l[5], Confidence=l[6])


if __name__ == "__main__":
    add_data()
