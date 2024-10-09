import pandas as pd
phage = pd.read_csv('/home/platform/phage_db/phage_api/workspace/csv_data/Download/Phage_meta_data/all_phage_meta_data_v2.tsv', sep='\t')
cluster=pd.read_csv('/home/platform/phage_db/phage_api/workspace/data_revision/clustering_result.txt', sep='\t',header=None)
cluster[1]=cluster[1].str.replace('group','cluster')
cluster[2]=cluster[2].str.replace('cluster','subcluster')
clusterdict=cluster.set_index(0)[1].to_dict()
subclusterDict=cluster.set_index(0)[2].to_dict()

for row in phage.itertuples():
        with open('/home/platform/phage_db/phage_data/data/phage_sequence/phage_fasta/'+row.Phage_source+'/'+row.Phage_ID+'.fasta', 'r') as f:
                content = f.read()
                with open('/home/platform/phage_db/phage_data/data/phage_sequence/cluster_v2/'+clusterdict[row.Phage_ID]+'.fasta', 'a') as cf:
                        cf.write(content)
                with open('/home/platform/phage_db/phage_data/data/phage_sequence/subcluster_v2/'+subclusterDict[row.Phage_ID]+'.fasta', 'a') as cf:
                        cf.write(content)







