import subprocess
import os
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import *
from tqdm import tqdm
from collections import Counter
import re

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
    # keywords, word2cwe = read_key_words("/home/sub3-wm/wzc/crawl/java_data/cxy_word2cwe.json")
    keywords = ['feat:', 'fix:', 'perf:', 'refactor:', 'style:', 'test:' ]
    word2cwe = None
    print(keywords)
    print(word2cwe)
    matched_commits = []
    repos_list = os.listdir('../java_data/repos')
    for repo in repos_list:
        repo_path = f"/home/sub3-wm/wzc/crawl/java_data/repos/{repo}"
        try:
            matched_commits_ = get_bug_fix_commits(repo_path, keywords, word2cwe)
            matched_commits += matched_commits_
            print(f"Found {len(matched_commits_)} matched commits in {repo}")
        except Exception as e:
            print(f"Error happened in {repo}: {e}")
            continue
    with open(f'matched_commits_cwe_1019repos_no_chinese.json', 'w') as f:
        json.dump(matched_commits, f, indent=4)
        
    print(f"Found {len(matched_commits)} matched commits in total.")
    print(f"Total repos: {len(repos_list)}")
    print("Done.")
    
def count_meta_data(json_path):
    with open(json_path, 'r') as f:
        datas = json.load(f)
    java_files = []
    save_data = []
    for data in datas:
        file_list = data['modified_files']
        cnt_java = 0
        for file in file_list:
            # print(file)
            if file.endswith('.java'):
                cnt_java += 1
        print(f"file nums: {len(file_list)}, java file nums: {cnt_java}")
        java_files.append(cnt_java)
        if 0 < cnt_java <= 1:
            save_data.append(data)
        

    cnt = Counter(java_files)
    
    cnt_1_10 = 0
    cnt_10 = 0
    for c in cnt:
        print(f"java file nums: {c}, cnt: {cnt[c]}")
        if 0< c <= 10:
            cnt_1_10 += cnt[c]
        if c > 10:
            cnt_10 += cnt[c]
    print(cnt)        
    print(f"java file nums <= 10: {cnt_1_10}")
    print(f"java file nums > 10: {cnt_10}")
    
    # with open(f'matched_commits_cwe_1019repos_filtered_english_filtered_file_1.json', 'w') as f:
    #     json.dump(save_data, f, indent=4)
            

def change_format_diff_to_target(json_path):
    with open(json_path, 'r') as f:
        datas = json.load(f)
    for data in datas:
        diff = data['diff']
        files = data['modified_files']
        for file in files:
            prefix = "--- a/" + file + "\n" + "+++ b/" + file + "\n"
            diff = prefix + diff
        converted_text =convert_to_target_format(diff)
        data['diff'] = converted_text
        
    with open(json_path, 'w') as f:
        json.dump(datas, f, indent=4)
    
def count_meta_info(json_path):
    with open(json_path, 'r') as f:
        datas = json.load(f)
    
    type = []
    for data in datas:
        type.append(data["keywords"][0])
        
    cnt = Counter(type)
    print(cnt)
    
#  todo add check chinese in message






if __name__ == '__main__':
    # get_java_repos()
    # repos_file_path = "/home/sub3-wm/wzc/crawl/java_data/added_java_repos.json"
    # clone_repos(repos_file_path)
    # get_matched_commit()
    
    # total_repos = 1000 
    # with open(f"./top_repo/top_java_repos_{total_repos}.json", 'r') as f:
    #     top_java_repos = json.load(f)
        
    # filtered_java_tools = filter_java_tools(top_java_repos)
    # with open(f"filter_top_java_repos_{total_repos}.json", 'w') as f:
    #     json.dump(filtered_java_tools, f, indent=4)
        
    # for repo in filtered_java_tools:
    #     print(f"Name: {repo['name']}, URL: {repo['html_url']}")
    
    count_meta_data("/home/sub3-wm/wzc/crawl/VulDataset-Collection/matched_commits_cwe_1019repos_no_chinese.json")
    
    # json_path = "/home/sub3-wm/wzc/crawl/VulDataset-Collection/matched_commits_cwe_1019repos_filtered_file_1.json"
    # change_format_diff_to_target(json_path)
    
    
    # count_meta_info("/home/sub3-wm/wzc/crawl/VulDataset-Collection/matched_commits_cwe_1019repos_filtered_file_1.json")
    # 示例
    # print(contains_chinese("Hello, 世界"))  # True
    # print(contains_chinese("Hello, World"))  # False