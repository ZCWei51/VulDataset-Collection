import subprocess
import os
import requests
import time
from git import Repo
import json,csv

access_token = ""
# 添加访问凭证到请求头部
headers = {"Authorization": f"Bearer {access_token}"}

"""
Read json file 
input: json file
output: json data
"""
def read_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

"""
Read csv file by column
input: csv file, column
output: column data
"""
def read_first_column(csv_file, column):
    # first_column = []
    first_column = set()

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            first_column.add(row[column])

    return first_column

"""
Get top repositories by language from github
input: language, per_page, total_repos
output: top_repos
"""
def get_top_java_repos(language="Java", per_page=100, total_repos=1000):
    top_repos = []
    page = 1
    base_url = "https://api.github.com/search/repositories"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {access_token}"
    }
    wait_time = 10  # GitHub 速率限制等待时间

    while len(top_repos) < total_repos:
        print(f"total_repos: {len(top_repos)} / total_repos: {total_repos}")
        params = {
            "q": f"language:{language}",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page,
            "page": page
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        time.sleep(wait_time)
        # 检查速率限制
        if response.status_code == 403:
            print("Rate limit reached. Waiting to retry...")
            time.sleep(wait_time)
            wait_time *= 2
            continue

        response.raise_for_status()
        data = response.json()
        repos = data.get("items", [])
        
        if not repos:
            break

        top_repos.extend(repos)
        page += 1

    return top_repos[:total_repos]


"""
Filter repos from a list of repositories
input: repos, tool_keywords(saved keywords), tutorial_keywords(filter keywords)
output: filtered_repos
"""
def filter_java_tools(repos, tool_keywords, tutorial_keywords):


    filtered_repos = []
    for repo in repos:
        if repo.get("description", "") is None:
            continue
        description = repo.get("description", "").lower()  # 获取仓库描述并转换为小写
        
        # 检查是否包含工具关键词
        is_tool = any(keyword in description for keyword in tool_keywords)
        # 检查是否包含教程关键词
        is_tutorial = any(keyword in description for keyword in tutorial_keywords)

        # 仅在是工具类项目且非教程类项目时保留
        if is_tool and not is_tutorial:
            filtered_repos.append(repo)
    
    return filtered_repos

""""""
def clone_github_repo(github_url, target_dir):
    # 如果目标目录不存在，则创建目录
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    try:
        # 使用 git clone 命令克隆仓库到指定目录
        subprocess.run(["git", "clone", github_url, target_dir], check=True)
        print(f"Successfully cloned {github_url} to {target_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository: {e}")
        


def get_bug_fix_commits(repo_path, keywords):
    repo = Repo(repo_path)
    repo_name = repo_path.split("/")[-1]  # 提取仓库名称
    matched_commits = []

    if repo.bare:
        print("The repository is bare. Please provide a valid Git repository path.")
        return matched_commits

    for commit in repo.iter_commits():
        commit_message = commit.message.lower()
        matched_keywords = [kw for kw in keywords if kw in commit_message]
        # if commit.hexsha != '05d12682a39c9df36595cef86fdaf35d10103909':
        #     continue
        # print(commit.hexsha)
        # print(commit_message)
        # 如果有关键词匹配到当前提交消息
        if matched_keywords:
            matched_commits.append({
                "repo_name": repo_name,
                "commit_hash": commit.hexsha,
                "datetime": commit.authored_datetime.isoformat(),
                "commit_message": commit_message,
                "keywords": matched_keywords
            })

    return matched_commits

import requests

def get_cwe_from_cve(cve_id):
    """
    Given a CVE ID, fetch the corresponding CWE ID using the NVD API.
    
    Parameters:
    - cve_id (str): The CVE ID to look up (e.g., 'CVE-2021-34527').

    Returns:
    - cwe_id (str): The CWE ID associated with the CVE, or None if not found.
    """
    url = f"https://services.nvd.nist.gov/rest/json/cve/1.0/{cve_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # Attempt to parse JSON response
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Failed to decode JSON. Response might not be in JSON format.")
        print("Response content:", response.text)  # Show the actual response for debugging
        return None

    # Extract the CWE ID
    try:
        cwe_id = data['result']['CVE_Items'][0]['cve']['problemtype']['problemtype_data'][0]['description'][0]['value']
        return cwe_id
    except (IndexError, KeyError):
        print(f"No CWE ID found for {cve_id}.")
        return None
    
def get_cwe_from_nvd_(cve):
    cwe = []
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve}"
    # 发送 GET 请求获取提交的详细信息
    response = requests.get(url)
    try:
        if response.status_code == 200:
            # 解析响应的 JSON 数据
            nvd_data = response.json()
            # print(nvd_data)
            if len(nvd_data['vulnerabilities'])>0:
                if 'weaknesses' not in nvd_data['vulnerabilities'][0]['cve']:
                    cwe.append(False)
                    return cwe
            else:
                return [False]
            weakness = nvd_data['vulnerabilities'][0]['cve']['weaknesses']
            # print(weakness)
            for i in range(0, len(weakness)):
                description = weakness[i]['description']
                # print(description)
                for d in description:
                    cwe_id = d['value']
                    cwe.append(cwe_id)
        else:
            print("response.status_code != 200")
        return cwe
    except:
        print(f"Error happened in cve : {cve}")
        return [False]
    
        
if __name__ == '__main__':  
    pass  
    # clone_github_repo("https://github.com/Snailclimb/JavaGuide", '/home/sub3-wm/wzc/crawl/java_data/repos')
    
    # 定义关键词
    # keywords = ["fix", "bug", "vulnerable", "patch", "error", "issue"]

    # # 使用示例
    # # repo_path = "/home/sub3-wm/wzc/crawl/java_data/repos/antlr4"  # 本地仓库路径
    # repo_path = "/home/sub3-wm/wzc/crawl/java_data/repos/RxJava"  # 本地仓库路径
    # matched_commits = get_bug_fix_commits(repo_path, keywords)
    # with open('matched_commits_rxjava.json', 'w') as f:
    #     json.dump(matched_commits, f, indent=4)
    # # 打印匹配结果
    # for commit_info in matched_commits:
    #     print(f"Repo: {commit_info['repo_name']}")
    #     print(f"Commit Hash: {commit_info['commit_hash']}")
    #     print(f"Matched Keywords: {', '.join(commit_info['keywords'])}")
    #     print("-" * 50)
    
    # Example usage
    cve_id = "CVE-2021-34527"
    cwe_id = get_cwe_from_nvd_(cve_id)
    if cwe_id:
        print(f"The CWE ID for {cve_id} is: {cwe_id}")
    else:
        print(f"Could not retrieve CWE ID for {cve_id}.")
