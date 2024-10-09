f_in = open("/home/platform/phage_db/phage_api/workspace/data_revision/protein/01.CHVD/sequence.gff3")
for line in f_in:
    if line.startswith("##"):
        continue
    if line.startswith("# Sequence Data"):
        acc = line.split('"')[1]
        source = 'CHVD'
        f = open("%s%s/%s.gff3"%('/home/platform/phage_db/phage_data/data/phage_sequence/phage_gff3/individual_data/',source, acc), "w")
        f.write(line)
    elif line == "\n":
        f.close()
    else:
        f.write(line)