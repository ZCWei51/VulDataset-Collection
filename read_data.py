import json
from utils import *

datas = read_json("/data/wzc/datasets/java_data/processed_Java.json")

save_data = []

for data in datas:
    cve_id = data['cve']
    cwe_id = data['vulnerability_type']
    save_data.append({
        'cve_id': cve_id,
        'cwe_id': cwe_id
    })
    
with open('cve2cwe_test.json', 'w') as f:
    json.dump(save_data, f, indent=4)
