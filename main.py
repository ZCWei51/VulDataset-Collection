import subprocess
import os
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import *
from tqdm import tqdm
def get_java_repos():
    total_repos = 1000
    per_page = 100
    top_java_repos = get_top_java_repos(language="Java", per_page=per_page, total_repos=total_repos)
    with open(f"top_java_repos_{total_repos}.json", 'w') as f:
        json.dump(top_java_repos, f, indent=4)
    filtered_java_tools = filter_java_tools(top_java_repos)
    with open(f"filter_top_java_repos_{total_repos}.json", 'w') as f:
        json.dump(filtered_java_tools, f, indent=4)
        
    for repo in filtered_java_tools:
        print(f"Name: {repo['name']}, URL: {repo['html_url']}")
        
def clone_repos(repos_file_path):
    with open(repos_file_path, 'r') as f:
        repos = json.load(f)

    # 使用 ThreadPoolExecutor 创建多线程池
    with ThreadPoolExecutor(max_workers=5) as executor:  # 设置适当的线程数量
        futures = []
        
        if "top" in repos_file_path:
            # 提交克隆任务到线程池
            for repo in repos:
                name = repo['name']
                url = repo['html_url']
                target_dir = f"repos/{name}"
                print(f"Submitting clone task for {name} from {url} to {target_dir}")
                futures.append(executor.submit(clone_github_repo, url, target_dir))
        else:
            for repo in repos:
                owner = repo['owner']
                name = repo['repo']
                url = f"https://github.com/{owner}/{name}"
                target_dir = f"repos/{name}"
                print(f"Submitting clone task for {name} from {url} to {target_dir}")
                futures.append(executor.submit(clone_github_repo, url, target_dir))

               
        # 使用 tqdm 显示进度条并等待所有任务完成
        for future in tqdm(as_completed(futures), total=len(futures)):
            future.result()  # 捕获克隆的结果或异常

# 调用 clone_repos 函数启动克隆
# clone_repos()
def read_key_words(file_path):
    datas = read_json(file_path)
    keywords = []
    for key, val in datas.items():
        keywords.append(key)
        
    return keywords, datas
def get_matched_commit():
    # 定义关键词
    # keywords = ["fix", "bug", "vulnerable", "patch", "error", "issue"]
    # keywords, word2cwe = read_key_words("/home/sub3-wm/wzc/crawl/java_data/word2cwe.json")
    keywords, word2cwe = read_key_words("/home/sub3-wm/wzc/crawl/java_data/cxy_word2cwe.json")
    # keywords = ['feat:', 'fix:', 'perf:', 'refactor:', 'style:', 'test:' ]
    # word2cwe = None
    print(keywords)
    print(word2cwe)
    matched_commits = []
    repos_list = os.listdir('repos')
    for repo in repos_list:
        repo_path = f"/home/sub3-wm/wzc/crawl/java_data/repos/{repo}"
        try:
            matched_commits_ = get_bug_fix_commits(repo_path, keywords, word2cwe)
            matched_commits += matched_commits_
            print(f"Found {len(matched_commits_)} matched commits in {repo}")
        except Exception as e:
            print(f"Error happened in {repo}: {e}")
            continue
    with open(f'matched_commits_cwe_cxy.json', 'w') as f:
        json.dump(matched_commits, f, indent=4)
        
    print(f"Found {len(matched_commits)} matched commits in total.")
    print(f"Total repos: {len(repos_list)}")
    print("Done.")
if __name__ == '__main__':
    # get_java_repos()
    # repos_file_path = "/home/sub3-wm/wzc/crawl/java_data/added_java_repos.json"
    # clone_repos(repos_file_path)
    get_matched_commit()
    
    # total_repos = 1000 
    # with open(f"./top_repo/top_java_repos_{total_repos}.json", 'r') as f:
    #     top_java_repos = json.load(f)
        
    # filtered_java_tools = filter_java_tools(top_java_repos)
    # with open(f"filter_top_java_repos_{total_repos}.json", 'w') as f:
    #     json.dump(filtered_java_tools, f, indent=4)
        
    # for repo in filtered_java_tools:
    #     print(f"Name: {repo['name']}, URL: {repo['html_url']}")