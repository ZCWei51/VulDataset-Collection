# VulDataset-Build
构建数据集用

# 函数说明
1. `get_java_repos(total_repos, language, saved_keywords, filter_keywords)`
- 功能：从 GitHub 获取 Java 仓库，根据关键词进行过滤，并保存结果。
- 参数：
    - total_repos (int)：要获取的总仓库数量。
    - language (str)：要搜索的编程语言（默认为 Java）。
    - saved_keywords (list of str)：保存结果时筛选的关键词。
    - filter_keywords (list of str)：用于排除教程和示例项目的关键词。
- 输出：
    - top_java_repos_{total_repos}.json：包含所有 Java 仓库的信息。
    - filter_top_java_repos_{total_repos}.json：过滤后的 Java 工具库信息。
2. `clone_repos(total_repos)`
- 功能：根据获取的仓库列表，多线程克隆符合条件的仓库。
- 参数：
    - total_repos (int)：要克隆的仓库数量。
- 输出：
    - 在本地 repos/ 目录中保存克隆的仓库。

3. `get_matched_commit(keywords)`
- 功能：在克隆的仓库中搜索提交信息，筛选包含特定关键词的提交。
- 参数：
    - keywords (list of str)：用于匹配提交信息的关键词列表。
- 输出：
    - matched_commits.json：包含匹配到的提交记录的 JSON 文件。
- 说明：遍历 repos/ 目录中的每个仓库，在提交信息中查找符合关键词的记录并保存。

4. utils.py line8 需要添加GitHub token