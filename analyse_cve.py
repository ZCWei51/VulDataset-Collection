import json
from utils import *

def categorize_by_cwe(data):
    """
    Categorizes a list of CVE-CWE data by CWE ID.
    
    Parameters:
    - data (list of dict): List of dictionaries containing CVE and CWE IDs.

    Returns:
    - dict: Dictionary with CWE IDs as keys and lists of CVE IDs as values.
    """
    categorized_data = {}
    
    for entry in data:
        cwe_ids = entry['cwe_id']
        cve_id = entry['cve_id']
        
        # Initialize list for this CWE ID if it doesn't exist
        for cwe_id in cwe_ids:
            if cwe_id not in categorized_data:
                categorized_data[cwe_id] = []
        
        # Append the CVE ID to the CWE category
        categorized_data[cwe_id].append(cve_id)
    
    for key, val in categorized_data.items():
        print(val)
        categorized_data[key] = list(set(val))
    
    return categorized_data
def main():
    json_file = '/data/wzc/datasets/CVEfixes/cve2cwe_CVEfixes.json'
    # json_file = '/data/wzc/crawler1/cve2cwe_ReposVul.json'
    # json_file = '/data/wzc/datasets/java_data/veracode/cve2cwe_veracode.json'
    datas = read_json(json_file)
    categorized_data = categorize_by_cwe(datas)
    with open('categorized_cwe_data_cvefixes.json', 'w') as f:
        json.dump(categorized_data, f, indent=4)
    


def update_data(data1, data2):
    for key, val in data2.items():
        if key in data1:
            data1[key].extend(val)
        else:
            data1[key] = val
    return data1
def merge_json():
    json_file1 = '/data/wzc/datasets/java_data/categorized_cwe_data_ReposVul.json'
    json_file2 = '/data/wzc/datasets/java_data/categorized_cwe_data_veracode.json'
    json_file3 = '/data/wzc/datasets/java_data/raw_data/cwe_map2_cve.json'
    json_file4 = '/data/wzc/datasets/java_data/categorized_cwe_data_cvefixes.json'
    
    json_file_save = '/data/wzc/datasets/java_data/categorized_cwe_data.json'    
    datas1 = read_json(json_file1)
    datas2 = read_json(json_file2)
    datas3 = read_json(json_file3)
    datas4 = read_json(json_file4)
    datas1 = update_data(datas1, datas2)
    datas1 = update_data(datas1, datas3)
    datas1 = update_data(datas1, datas4)
    
    # remove duplicate
    for key, val in datas1.items():
        datas1[key] = list(set(val))
    
    with open(json_file_save, 'w') as f:
        json.dump(datas1, f, indent=4)
        
    print(len(datas1))
    total = 0
    for key, val in datas1.items():
        print(key, len(val))
        total += len(val)
    print(total)

if __name__ == "__main__":
    # main()
    merge_json()