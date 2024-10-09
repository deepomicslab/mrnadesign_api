from phage.models import phage
from phage_protein.models import phage_protein_NCBI, phage_protein_PhagesDB, phage_protein_GPD, phage_protein_MGV, phage_protein_TemPhD, phage_protein_GVD,phage_protein_IMG_VR,phage_protein_CHVD,phage_protein_IGVD,phage_protein_GOV2,phage_protein_STV
from phage_protein.serializers import phage_protein_GPD_Serializer, phage_protein_GVD_Serializer, phage_protein_MGV_Serializer, phage_protein_NCBI_Serializer, phage_protein_PhagesDB_Serializer, phage_protein_TemPhD_Serializer,phage_protein_IMG_VR_Serializer,phage_protein_CHVD_Serializer,phage_protein_IGVD_Serializer,phage_protein_GOV2_Serializer,phage_protein_STV_Serializer

from phage_protein.models import phage_protein_tmhmm_NCBI, phage_protein_tmhmm_PhagesDB, phage_protein_tmhmm_GPD, phage_protein_tmhmm_MGV, phage_protein_tmhmm_TemPhD, phage_protein_tmhmm_GVD,phage_protein_tmhmm_IMG_VR,phage_protein_tmhmm_CHVD,phage_protein_tmhmm_IGVD,phage_protein_tmhmm_GOV2,phage_protein_tmhmm_STV
from phage_protein.serializers import phage_protein_tmhmm_NCBI_Serializer, phage_protein_tmhmm_PhagesDB_Serializer, phage_protein_tmhmm_GPD_Serializer, phage_protein_tmhmm_MGV_Serializer, phage_protein_tmhmm_TemPhD_Serializer, phage_protein_tmhmm_GVD_Serializer,phage_protein_tmhmm_IMG_VR_Serializer,phage_protein_tmhmm_CHVD_Serializer,phage_protein_tmhmm_IGVD_Serializer,phage_protein_tmhmm_GOV2_Serializer,phage_protein_tmhmm_STV_Serializer
def findphageprotein(phageAccId=None,phageId=None):
    """
    Find phage protein in database
    """
    if phageId is None:
        phages = phage.objects.get(Acession_ID=phageAccId)
    else:
        phages = phage.objects.get(id=phageId)

    if phages.Data_Sets.id <= 5:
        proteins = phage_protein_NCBI.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_NCBI_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 6:
        proteins = phage_protein_PhagesDB.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_PhagesDB_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 7:
        proteins = phage_protein_GPD.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_GPD_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 8:
        proteins = phage_protein_GVD.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_GVD_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 9:
        proteins = phage_protein_MGV.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_MGV_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 10:
        proteins = phage_protein_TemPhD.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_TemPhD_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 11:
        proteins = phage_protein_CHVD.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_CHVD_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 12:
        proteins = phage_protein_IGVD.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_IGVD_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 13:
        proteins = phage_protein_IMG_VR.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_IMG_VR_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 14:
        proteins = phage_protein_GOV2.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_GOV2_Serializer(proteins, many=True)
    elif phages.Data_Sets.id == 15: 
        proteins = phage_protein_STV.objects.filter(
            Phage_Acession_ID=phages.Acession_ID)
        serializer = phage_protein_STV_Serializer(proteins, many=True)
        
    return serializer.data


def findPhageProteinDetail(phageAccId,proteinId):
    """
    Find phage protein detail in database
    """
    phageObject = phage.objects.get(Acession_ID=phageAccId)
    if phageObject.Data_Sets.id <= 5:
        proteins = phage_protein_NCBI.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_NCBI_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 6:
        proteins = phage_protein_PhagesDB.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_PhagesDB_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 7:
        proteins = phage_protein_GPD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_GPD_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 8:
        proteins = phage_protein_GVD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_GVD_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 9:
        proteins = phage_protein_MGV.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_MGV_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 10:
        proteins = phage_protein_TemPhD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_TemPhD_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 11:
        proteins = phage_protein_CHVD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_CHVD_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 12:
        proteins = phage_protein_IGVD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_IGVD_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 13:
        proteins = phage_protein_IMG_VR.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_IMG_VR_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 14:
        proteins = phage_protein_GOV2.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_GOV2_Serializer(proteins, many=True)
    elif phageObject.Data_Sets.id == 15:
        proteins = phage_protein_STV.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID, Protein_id=proteinId)
        serializer = phage_protein_STV_Serializer(proteins, many=True)

    return serializer.data


def findPhageTransProtein(phageId):
    """
    Find phage transprotein detail in database
    """
    phageObject = phage.objects.get(id=phageId)

    if phageObject.Data_Sets.id <= 5:
        proteins = phage_protein_tmhmm_NCBI.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_NCBI_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 6:
        proteins = phage_protein_tmhmm_PhagesDB.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_PhagesDB_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 7:
        proteins = phage_protein_tmhmm_GPD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_GPD_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 8:
        proteins = phage_protein_tmhmm_GVD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_GVD_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 9:
        proteins = phage_protein_tmhmm_MGV.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_MGV_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 10:
        proteins = phage_protein_tmhmm_TemPhD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_TemPhD_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 11:
        proteins = phage_protein_tmhmm_CHVD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_CHVD_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 12:
        proteins = phage_protein_tmhmm_IGVD.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_IGVD_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 13:
        proteins = phage_protein_tmhmm_IMG_VR.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_IMG_VR_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 14:
        proteins = phage_protein_tmhmm_GOV2.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_GOV2_Serializer(
            proteins, many=True)
    elif phageObject.Data_Sets.id == 15:
        proteins = phage_protein_tmhmm_STV.objects.filter(
            Phage_Acession_ID=phageObject.Acession_ID)
        serializer = phage_protein_tmhmm_STV_Serializer(
            proteins, many=True)
    return serializer.data