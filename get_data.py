import requests
import csv

def get_data():
    src_url = "https://api.sourceclear.com/catalog/search?q=language%3Ajava%20type%3Avulnerability&page={}"
    for i in range(1, 2):
        target_url = src_url.format(i)
        r = requests.get(target_url)
        print(target_url)
        print(r)
        print(r.status_code)
        print(r.json())
        if r.status_code == 503:
            break
        try:
            contents = r.json()["contents"]
        except KeyError:
            break
        for cve in contents:
            if cve["model"]["cve"] == None:
                continue
            CVE_id = "CVE-" + cve["model"]["cve"]
            print(CVE_id)
            try:
                for component in cve["model"]["artifactComponents"]:
                    if component["componentCoordinateType"] != "MAVEN":
                        continue
                    component_id = component["componentName"]
                    for versionRange in component["versionRanges"]:
                        if versionRange["patch"] == "" or versionRange["patch"] == None:
                            continue
                        version_range = versionRange["versionRange"]
                        patch = versionRange["patch"]
                        writer.writerow([CVE_id, component_id, version_range, patch])
            except KeyError:
                continue
                    

# cveid, component_id, version_range, patch
if __name__ == "__main__":
    f = open('./Java-Data.csv', 'w')
    writer = csv.writer(f)
    get_data()
    f.close()