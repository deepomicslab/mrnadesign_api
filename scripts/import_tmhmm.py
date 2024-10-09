import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Phage_api.settings")

django.setup()
# ['Genbank', 'RefSeq', 'DDBJ', 'EMBL', 'tpg', 'PhagesDB', 'GPD', 'GVD', 'MGV', 'TemPhD']


def add_data():
    from phage_protein.models import phage_protein_tmhmm_NCBI, phage_protein_tmhmm_PhagesDB, phage_protein_tmhmm_GPD, phage_protein_tmhmm_MGV, phage_protein_tmhmm_TemPhD, phage_protein_tmhmm_GVD
    baseurl = '/home/platform/phage_db/phage_api/workspace/csv_data/trans/'
    # dataset = ['ncbi', '6', '7', '8', '9', '10']
    # ncbi,6,8 10
    dataset = ['8', '9', '10']
    for i in dataset:
        print(i)
        with open(baseurl+i+'.csv', 'r') as f:
            lines = f.readlines()

        for line in lines:
            if 'phageid' in line:
                continue
            else:
                l = line.strip().split("\t")
                # phageid	Length	predictedTMHsNumber	ExpnumberofAAsinTMHs	Expnumberfirst60AAs	TotalprobofNin	POSSIBLENterm	insidesource	insidestart	insideend	TMhelixsource	TMhelixstart	TMhelixend	outsidesource	outsidestart	outsideend	proteinid
                if i == 'ncbi':
                    phage_protein_tmhmm_NCBI.objects.create(
                        Phage_Acession_ID=l[0], Length=l[1], predictedTMHsNumber=l[2], ExpnumberofAAsinTMHs=l[3], Expnumberfirst60AAs=l[4], TotalprobofNin=l[5], POSSIBLENterm=l[6], insidesource=l[7], insidestart=l[8], insideend=l[9], TMhelixsource=l[10], TMhelixstart=l[11], TMhelixend=l[12], outsidesource=l[13], outsidestart=l[14], outsideend=l[15], Protein_id=l[16])
                elif i == '6':
                    phage_protein_tmhmm_PhagesDB.objects.create(
                        Phage_Acession_ID=l[0], Length=l[1], predictedTMHsNumber=l[2], ExpnumberofAAsinTMHs=l[3], Expnumberfirst60AAs=l[4], TotalprobofNin=l[5], POSSIBLENterm=l[6], insidesource=l[7], insidestart=l[8], insideend=l[9], TMhelixsource=l[10], TMhelixstart=l[11], TMhelixend=l[12], outsidesource=l[13], outsidestart=l[14], outsideend=l[15], Protein_id=l[16])
                elif i == '7':
                    phage_protein_tmhmm_GPD.objects.create(
                        Phage_Acession_ID=l[0], Length=l[1], predictedTMHsNumber=l[2], ExpnumberofAAsinTMHs=l[3], Expnumberfirst60AAs=l[4], TotalprobofNin=l[5], POSSIBLENterm=l[6], insidesource=l[7], insidestart=l[8], insideend=l[9], TMhelixsource=l[10], TMhelixstart=l[11], TMhelixend=l[12], outsidesource=l[13], outsidestart=l[14], outsideend=l[15], Protein_id=l[16])
                elif i == '8':
                    phage_protein_tmhmm_GVD.objects.create(
                        Phage_Acession_ID=l[0], Length=l[1], predictedTMHsNumber=l[2], ExpnumberofAAsinTMHs=l[3], Expnumberfirst60AAs=l[4], TotalprobofNin=l[5], POSSIBLENterm=l[6], insidesource=l[7], insidestart=l[8], insideend=l[9], TMhelixsource=l[10], TMhelixstart=l[11], TMhelixend=l[12], outsidesource=l[13], outsidestart=l[14], outsideend=l[15], Protein_id=l[16])
                elif i == '9':
                    phage_protein_tmhmm_MGV.objects.create(
                        Phage_Acession_ID=l[0], Length=l[1], predictedTMHsNumber=l[2], ExpnumberofAAsinTMHs=l[3], Expnumberfirst60AAs=l[4], TotalprobofNin=l[5], POSSIBLENterm=l[6], insidesource=l[7], insidestart=l[8], insideend=l[9], TMhelixsource=l[10], TMhelixstart=l[11], TMhelixend=l[12], outsidesource=l[13], outsidestart=l[14], outsideend=l[15], Protein_id=l[16])
                elif i == '10':
                    phage_protein_tmhmm_TemPhD.objects.create(
                        Phage_Acession_ID=l[0], Length=l[1], predictedTMHsNumber=l[2], ExpnumberofAAsinTMHs=l[3], Expnumberfirst60AAs=l[4], TotalprobofNin=l[5], POSSIBLENterm=l[6], insidesource=l[7], insidestart=l[8], insideend=l[9], TMhelixsource=l[10], TMhelixstart=l[11], TMhelixend=l[12], outsidesource=l[13], outsidestart=l[14], outsideend=l[15], Protein_id=l[16])


if __name__ == "__main__":
    add_data()
