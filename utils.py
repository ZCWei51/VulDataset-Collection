import subprocess
import os
import requests
import time
from git import Repo
import json,csv
import json

def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
access_token = ""
# 添加访问凭证到请求头部
headers = {"Authorization": f"Bearer {access_token}"}


def read_first_column(csv_file, column):
    # first_column = []
    first_column = set()

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            first_column.add(row[column])

    return first_column

def get_top_java_repos_(language="Java", total_repos=5000, current_year=2025):
    collected_repos = []
    base_url = "https://api.github.com/search/repositories"
    headers = {"Authorization": f"Bearer {access_token}"}
    # current_year = datetime.now().year
    start_year = max(current_year - 10, 2008)  # 限制最早年份
    wait_time = 30  # 初始等待时间
    
    # 时间分片：近15年数据
    for year in range(current_year, start_year - 1, -1):
        # 动态生成结束日期
        if year == current_year:
            end_date = datetime.now().strftime("%Y-%m-%d")
        else:
            end_date = f"{year}-12-31"
        
        time_range = f"created:{year}-01-01..{end_date}"
        stars_ranges = [
            ("stars:>=10000", None),
            ("stars:5000..9999", 10000),
            ("stars:4000..4999", 5000),
            ("stars:3000..3999", 4000),
            # ("stars:2000..2999", 3000),
            # ("stars:1000..1999", 2000),
            # ("stars:900..999", 1000),
            # ("stars:800..899", 900),
            # ("stars:700..799", 800),
            # ("stars:600..699", 700),
            # ("stars:500..599", 600),
            # ("stars:400..499", 500),
            # ("stars:300..399", 400),
            # ("stars:200..299", 300),
            # ("stars:100..199", 200),
            # ("stars:50..100", 100)
        ]
        
        def generate_star_ranges(min_star=100, max_star=1000, step=100):
            """动态生成星数分段，支持自定义间隔
            Args:
                min_star: 最低星数段的下界 (默认100)
                max_star: 最高星数段的上界 (默认1000)
                step: 星数间隔 (默认100)
            Returns:
                List[Tuple]: 生成的星数范围列表
            """
            ranges = []
            current = max_star
            
            # 动态生成指定区间段（默认100-1000）
            while current >= min_star + step:
                lower = current - step + 1
                upper = current
                ranges.append(
                    (f"stars:{lower}..{upper}", current + 1)
                )
                current -= step
            
            # 添加兜底段（包含剩余星数）
            ranges.append(
                (f"stars:>={min_star}", min_star + step)
            )
            
            return ranges
        # 生成star 范围
        # 1000-2000 step 200
        stars_ranges.extend(generate_star_ranges(1000,3000,200))
        # 100-1000 step 10
        stars_ranges.extend(generate_star_ranges(100,1000,10))
        
        # print(f"stars_ranges: {stars_ranges}")
        # continue
        # Stars 分片
        for stars_query, upper_bound in stars_ranges:
            page = 1
            max_pages = 10  # GitHub 限制
            
            while page <= max_pages:
                query = f"language:{language} {time_range} {stars_query}"
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 100,
                    "page": page
                }
                
                # 带重试机制的请求
                for _ in range(3):  # 最大重试3次
                    response = requests.get(base_url, headers=headers, params=params)
                    if response.status_code == 403:
                        reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                        sleep_duration = max(reset_time - time.time(), 60)
                        print(f"Rate limit hit. Sleeping for {sleep_duration} seconds")
                        time.sleep(sleep_duration)
                        continue
                    break
                
                response.raise_for_status()
                data = response.json()
                repos = data.get("items", [])
                
                # 过滤低星仓库
                if repos and upper_bound:
                    repos = [r for r in repos if r['stargazers_count'] < upper_bound]
                
                if not repos:
                    break
                
                # 去重处理
                new_repos = [
                    r for r in repos 
                    if r['id'] not in {x['id'] for x in collected_repos}
                ]
                collected_repos.extend(new_repos)
                
                # 进度控制
                print(f"Year: {year}, Stars: {stars_query}, Page: {page} | Total collected: {len(collected_repos)}")
                if len(collected_repos) >= total_repos:
                    return sorted(collected_repos, key=lambda x: -x['stargazers_count'])[:total_repos]
                
                page += 1
                time.sleep(wait_time)  # 基础间隔防止触发限制
        # save by year
        with open(f"tmp_top_java_repos_{year}.json", 'w') as f:
            json.dump(collected_repos, f, indent=4)
    # 最终排序截取
    final_repos = sorted(collected_repos, key=lambda x: -x['stargazers_count'])
    return final_repos[:total_repos]


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
def filter_java_tools(repos):
    # 定义工具项目关键词和教程排除关键词
    tool_keywords = ["tool", "library", "framework", "sdk", "api", "plugin", "module"]
    tutorial_keywords = ["tutorial", "example", "learn", "guide", "demo", "sample", "practice",
                         "学习", "指南", "面试", "教程", "示例", "练习", "实例", "样例", "范例"]

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
        # if is_tool and not is_tutorial:
        # 非教程类项目时保留
        if not is_tutorial:
            filtered_repos.append(repo)
    
    return filtered_repos

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
        
def contains_chinese(string):
    # 使用正则表达式匹配中文字符的范围
    chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_char_pattern.search(string))

def get_bug_fix_commits(repo_path, keywords, word2cwe=None):
    repo = Repo(repo_path)
    remote_url = repo.remotes.origin.url

    repo_name = remote_url.split("/")[-1]  # 提取仓库名称
    owner_name = remote_url.split("/")[-2]  # 提取所有者
    matched_commits = []

    if repo.bare:
        print("The repository is bare. Please provide a valid Git repository path.")
        return matched_commits

    for commit in repo.iter_commits():
        commit_message = commit.message.lower()
        if contains_chinese(commit_message):
            continue
        # matched_keywords = [kw for kw in keywords if kw in commit_message.lower()]
        # matched_keywords = [kw for kw in keywords if commit_message.lower().startswith(kw)]
        matched_keywords = [kw for kw in keywords if kw in commit_message.lower()]
        # if commit.hexsha != '05d12682a39c9df36595cef86fdaf35d10103909':
        #     continue
        # print(commit.hexsha)
        # print(commit_message)
        # 如果有关键词匹配到当前提交消息
        


        if matched_keywords:
            cwe_list = []
            if word2cwe is not None:
                for matched_keyword in matched_keywords:
                    cwe_list.append(word2cwe[matched_keyword])
                    
            # 统计修改的文件和 hunk 信息
            modified_files = []
            total_hunks = 0
            diff_content = ""
            # 获取父提交（diff 需要和父提交比较）
            parents = commit.parents
            if parents:
                parent_commit = parents[0]
                diff_index = commit.diff(parent_commit, create_patch=True)
                # print(f"diff_index {diff_index}")
                for diff in diff_index:
                    # print(f"diff content {diff}")
                    if diff.a_path:  # 获取修改的文件路径
                        modified_files.append(diff.a_path)
                    # print(f"diff.diff {diff.diff}")
                    # 统计 hunk 数量
                    if diff.diff:  # diff.diff 是字节流
                        hunks = diff.diff.decode('utf-8', errors='ignore').count('@@')  # 每个 hunk 以 @@ 开始
                        total_hunks += hunks
                        diff_content = diff.diff.decode('utf-8', errors='ignore')
                        
            if contains_chinese(diff_content):
                continue       
            matched_commits.append({
                "repo_name": repo_name,
                "owner_name": owner_name,
                "commit_hash": commit.hexsha,
                "datetime": commit.authored_datetime.isoformat(),
                "commit_message": commit_message,
                "keywords": matched_keywords,
                "cwe": cwe_list,
                "diff":diff_content,
                "modified_files": modified_files,   # 修改的文件列表
                "total_hunks": total_hunks//2,      # hunk 的总数量
                "total_files": len(modified_files)  # 修改的文件数量
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
        
        
import re

def convert_to_target_format(diff_text):
    """
    Convert a standard diff format to the target custom format.

    Args:
    - diff_text (str): The standard diff format.

    Returns:
    - str: The converted target format.
    """
    lines = diff_text.splitlines()
    target_format = []
    current_file_a = None
    current_file_b = None
    code_lines = []

    # Patterns to extract file headers and modifications
    file_a_pattern = re.compile(r"^--- a/(.+)")
    file_b_pattern = re.compile(r"^\+\+\+ b/(.+)")
    context_pattern = re.compile(r"@@.*@@")
    
    for line in lines:
        if file_a_match := file_a_pattern.match(line):
            current_file_a = file_a_match.group(1).replace("/", " / ")
        elif file_b_match := file_b_pattern.match(line):
            current_file_b = file_b_match.group(1).replace("/", " / ")
        elif context_pattern.match(line):
            # Ignore the context line starting with @@
            continue
        elif line.startswith("-") or line.startswith("+") or line.strip():
            # Collect relevant code changes
            if line.startswith("-"):
                code_lines.append(f"- {line[1:].strip()}")  # Remove the `-` marker
            elif line.startswith("+"):
                code_lines.append(f"+ {line[1:].strip()}")  # Prefix with `+`
            else:
                code_lines.append(line.strip())  # For unchanged lines
    
    # Build the target format output
    if current_file_a and current_file_b:
        target_format.append(f"mmm a / {current_file_a} <nl>")
        target_format.append(f"ppp b / {current_file_b} <nl>")
    
    for code_line in code_lines:
        target_format.append(f"{code_line} <nl>")
    
    # Join the lines with space for final result
    return " ".join(target_format)

# Example input
# diff_text = """--- a/src/main/java/org/apache/ibatis/mapping/CacheBuilder.java
# +++ b/src/main/java/org/apache/ibatis/mapping/CacheBuilder.java
# @@ -100,7 +100,9 @@ public Cache build() {
#      setCacheProperties(cache);
#    }
#    cache = setStandardDecorators(cache);
# +  } else if (!LoggingCache.class.isAssignableFrom(cache.getClass())) {
# +    cache = new LoggingCache(cache);
#    }
#    return cache;
#  }
# """

# # Convert the diff to the target format
# converted_text = convert_to_target_format(diff_text)
# print(converted_text)

