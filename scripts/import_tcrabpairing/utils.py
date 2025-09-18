# i.e. zou yiping demo.ipynb 2025/9/12

import numpy as np
import pandas as pd
from typing import Literal, Optional
import tidytcells as tt

VALID_AMINO_ACIDS = set('ARNDCQEGHILKMFPSTWYV')

def convert_tcr_format_robust(df):

    # Separate TRA and TRB chain data
    tra_df = df[df['chain'] == 'TRA'].copy()
    trb_df = df[df['chain'] == 'TRB'].copy()
    
    # Check if there are other chain types
    other_chains = df[~df['chain'].isin(['TRA', 'TRB'])]['chain'].unique()
    if len(other_chains) > 0:
        print(f"Warning: Found other chain types {other_chains}, these data will be ignored")
    
    # Rename TRA chain columns
    tra_df = tra_df.rename(columns={
        'v_gene': 'TRAV',
        'j_gene': 'TRAJ',
        'cdr3': 'cdr3A',
        'cdr3_nt': 'cdr3_ntA',
        'reads': 'readsA',
        'umis': 'umisA'
    })
    
    # Rename TRB chain columns
    trb_df = trb_df.rename(columns={
        'v_gene': 'TRBV',
        'j_gene': 'TRBJ',
        'cdr3': 'cdr3B',
        'cdr3_nt': 'cdr3_ntB',
        'reads': 'readsB',
        'umis': 'umisB'
    })
    
    # Keep needed columns
    tra_cols = ['barcode', 'TRAV', 'TRAJ', 'cdr3A', 'cdr3_ntA', 'readsA', 'umisA']
    trb_cols = ['barcode', 'TRBV', 'TRBJ', 'cdr3B', 'cdr3_ntB', 'readsB', 'umisB', 'raw_clonotype_id']
    
    tra_df = tra_df[tra_cols]
    trb_df = trb_df[trb_cols]
    
    # Check if there are multiple TRA or TRB corresponding to the same barcode
    tra_counts = tra_df['barcode'].value_counts()
    trb_counts = trb_df['barcode'].value_counts()
    
    duplicated_tra = tra_counts[tra_counts > 1].index.tolist()
    duplicated_trb = trb_counts[trb_counts > 1].index.tolist()
    
    if duplicated_tra:
        print(f"Warning: Found {len(duplicated_tra)} barcodes with multiple TRA chains, the first occurrence of TRA will be kept for these")
        
    if duplicated_trb:
        print(f"Warning: Found {len(duplicated_trb)} barcodes with multiple TRB chains, the first occurrence of TRB will be kept for these")
    
    # Merge TRA and TRB data
    tra_df = tra_df.drop(duplicated_tra)
    tra_df = tra_df.drop(duplicated_trb)
    merged_df = pd.merge(tra_df, trb_df, on='barcode', how='outer')
    merged_df = merged_df.dropna(subset=tra_cols + trb_cols)
    
    return merged_df


def merge_chains_and_deduplicate(df):
    
    # 合併 Alpha 鏈信息
    df['Alpha'] = df.apply(
        lambda row: f"{row['TRAV']}_{row['cdr3_ntA']}_{row['TRAJ']}" 
        if pd.notna(row['TRAV']) and pd.notna(row['cdr3_ntA']) and pd.notna(row['TRAJ']) 
        else None, 
        axis=1
    )
    
    # 合併 Beta 鏈信息
    df['Beta'] = df.apply(
        lambda row: f"{row['TRBV']}_{row['cdr3_ntB']}_{row['TRBJ']}" 
        if pd.notna(row['TRBV']) and pd.notna(row['cdr3_ntB']) and pd.notna(row['TRBJ']) 
        else None, 
        axis=1
    )
    
    df = df[~df['Alpha'].isna() & ~df['Beta'].isna()]
    df['clonotype_freq'] = 1
    # 對於相同的 Alpha-Beta 配對，合併 umisA 和 umisB
    agg_dict = {}
    
    # 對於數值列（umisA, umisB），計算總和
    if 'umisA' in df.columns:
        agg_dict['umisA'] = 'mean'
    if 'umisB' in df.columns:
        agg_dict['umisB'] = 'mean'
    if 'clonotype_freq' in df.columns:
        agg_dict['clonotype_freq'] = 'sum'

    # 對於其他列，保留第一個值
    other_columns = [col for col in df.columns if col not in ['Alpha', 'Beta', 'umisA', 'umisB', 'clonotype_freq']]
    for col in other_columns:
        agg_dict[col] = 'first'
    
    # 按 Alpha 和 Beta 分組並聚合
    dedup_df = df.groupby(['Alpha', 'Beta'], dropna=False).agg(agg_dict).reset_index()
    dedup_df = dedup_df[~dedup_df['Alpha'].isna() & ~dedup_df['Beta'].isna()]
  
    return dedup_df

def process_10x_dataset(testdf):
    '''
    This is for pre-processing 10x dataset. 
    1. Only retain the productive cells expressing only one TCR.
    2. VL+JL+CDR3A + VL+JL+CDR3B should be unique. 
    '''
    #testdf = pd.read_csv(datapath, sep=",")
    filtered_tcr_file = testdf.loc[(testdf['is_cell'] ) & (testdf['high_confidence']) & (testdf['productive'])]
    filtered_tcr_file.cdr3.replace(to_replace='None', value=np.nan, inplace = True)
    filtered_tcr_file = filtered_tcr_file.dropna(subset=['cdr3_nt', 'cdr3', 'v_gene', 'j_gene'])
    filtered_tcr_file['v_gene'] = filtered_tcr_file['v_gene'].map(tt.tr.standardize)
    filtered_tcr_file['j_gene'] = filtered_tcr_file['j_gene'].map(tt.tr.standardize)
    chain_counts = filtered_tcr_file.groupby(['barcode', 'chain']).size().unstack(fill_value=0)
    valid_barcodes = chain_counts[(chain_counts.get('TRA', 0) == 1) & (chain_counts.get('TRB', 0) == 1)].index
    filtered_tcr_df = filtered_tcr_file[filtered_tcr_file['barcode'].isin(valid_barcodes)]
    filtered_tcr_df = filtered_tcr_df.dropna(subset=['cdr3_nt', 'cdr3', 'v_gene', 'j_gene'])
    filtered_tcr_df = filtered_tcr_df[filtered_tcr_df['cdr3'].str.match(r'^[ARNDCQEGHILKMFPSTWYV]*$', na=False)]
    filtered_tcr_df = convert_tcr_format_robust(filtered_tcr_df)
    filtered_tcr_df = merge_chains_and_deduplicate(filtered_tcr_df)
    
    return filtered_tcr_df