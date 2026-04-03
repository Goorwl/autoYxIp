import urllib.request
import urllib.parse

# 配置项
url = "https://zip.cm.edu.kg/all.txt"
MAX_LINES = 300

# 地区及其对应关键词字典 (key 就是最终生成的文件名)
regions_keywords = {
    "us": ["US", "美国", "UNITED STATES", "AMERICA"],
    "jp": ["JP", "日本", "JAPAN", "TOKYO", "OSAKA"],
    "sg": ["SG", "新加坡", "SINGAPORE", "狮城"],
    "hk": ["HK", "香港", "HONG KONG", "HONGKONG"],
    "tw": ["TW", "台湾", "TAIWAN", "TAIPEI", "新北"],
    "kr": ["KR", "韩国", "KOREA", "SEOUL"],
    "uk": ["UK", "英国", "UNITED KINGDOM", "LONDON"],
    "de": ["DE", "德国", "GERMANY", "FRANKFURT"],
    "fr": ["FR", "法国", "FRANCE", "PARIS"]
}

try:
    print("正在下载源文件...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    content = response.read().decode('utf-8')
    lines = content.splitlines()
    
    # 初始化存储结果的字典，格式: {"us": [], "jp": [], ...}
    results = {key: [] for key in regions_keywords}
    
    print("正在解析和分类节点...")
    for line in lines:
        # 核心优化：先 URL 解码，再转大写。解决 "%E7%BE%8E%E5%9B%BD" 这种编码导致搜不到中文的问题
        decoded_line_upper = urllib.parse.unquote(line).upper()
        
        for region, keywords in regions_keywords.items():
            # 如果该地区还没收集满，继续判断
            if len(results[region]) < MAX_LINES:
                # 只要包含该地区任意一个关键词，就判定为该地区
                if any(kw in decoded_line_upper for kw in keywords):
                    results[region].append(line) # 注意：这里保存的是原封不动的 line，确保链接可用
                    break # 匹配到一个国家后，跳出内层循环，避免一个节点分到两个文件
        
        # 检查是否所有的地区都收集满 MAX_LINES 了
        if all(len(results[r]) >= MAX_LINES for r in results):
            print("所有地区均已收集完毕，提前结束解析！")
            break

    # 批量写入对应的 txt 文件
    for region, data in results.items():
        filename = f"{region}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(data))
        print(f"成功生成 {filename}，共保留 {len(data)} 条记录。")

except Exception as e:
    print(f"发生错误: {e}")