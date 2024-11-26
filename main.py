import subprocess
import os
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import *
from tqdm import tqdm


def get_java_repos(total_repos, language, saved_keywords, filter_keywords):
    per_page = 100
    
    top_java_repos = get_top_java_repos(language=language, per_page=per_page, total_repos=total_repos)
    with open(f"top_java_repos_{total_repos}.json", 'w') as f:
        json.dump(top_java_repos, f, indent=4)
        
    filtered_java_tools = filter_java_tools(top_java_repos, saved_keywords, filter_keywords)
    with open(f"filter_top_java_repos_{total_repos}.json", 'w') as f:
        json.dump(filtered_java_tools, f, indent=4)
        
    for repo in filtered_java_tools:
        print(f"Name: {repo['name']}, URL: {repo['html_url']}")
        
def clone_repos(total_repos):
    with open(f"filter_top_java_repos_{total_repos}.json", 'r') as f:
        repos = json.load(f)

    if not os.path.exists("./repos"):
        os.makedirs("./repos")
        
    # 使用 ThreadPoolExecutor 创建多线程池
    with ThreadPoolExecutor(max_workers=5) as executor:  # 设置适当的线程数量
        futures = []
        
        # 提交克隆任务到线程池
        for repo in repos:
            name = repo['name']
            url = repo['html_url']
            target_dir = f"repos/{name}"
            print(f"Submitting clone task for {name} from {url} to {target_dir}")
            futures.append(executor.submit(clone_github_repo, url, target_dir))
        
        # 使用 tqdm 显示进度条并等待所有任务完成
        for future in tqdm(as_completed(futures), total=len(futures)):
            future.result()  # 捕获克隆的结果或异常


def get_matched_commit(keywords):
    matched_commits = []
    repos_list = os.listdir('repos')
    for repo in repos_list:
        repo_path = f"/home/sub3-wm/wzc/crawl/java_data/repos/{repo}"
        matched_commits_ = get_bug_fix_commits(repo_path, keywords)
        matched_commits += matched_commits_
        print(f"Found {len(matched_commits_)} matched commits in {repo}")
    with open(f'matched_commits.json', 'w') as f:
        json.dump(matched_commits, f, indent=4)
        
    print(f"Found {len(matched_commits)} matched commits in total.")
    print(f"Total repos: {len(repos_list)}")
    print("Done.")
if __name__ == '__main__':
    
    # total_repos = 1000
    # language = 'Java'
    # 定义工具项目关键词和教程排除关键词
    # saved_keywords = ["tool", "library", "framework", "sdk", "api", "plugin", "module"]
    # filter_keywords = ["tutorial", "example", "learn", "guide", "demo", "sample", "practice",
    #                      "学习", "指南", "面试", "教程", "示例", "练习", "实例", "样例", "范例"]
    # get_java_repos(total_repos, language,saved_keywords, filter_keywords)
    
    
    
    # clone_repos(total_repos)
    
    # 定义关键词
    keywords = ["fix", "bug", "vulnerable", "patch", "error", "issue"]
    get_matched_commit(keywords)
    
        

