import urllib.request

# 源网址
url = "https://zip.cm.edu.kg/all.txt"
output_file = "us.txt"

try:
    # 1. 下载源文件
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    content = response.read().decode('utf-8')

    # 2. 解析和过滤内容
    lines = content.splitlines()
    us_lines = []
    
    for line in lines:
        # 这里是过滤逻辑，你可以自己改。这里假设保留包含 "US", "us", "美国" 的行
        if "US" in line.upper() or "美国" in line:
            us_lines.append(line)

    # 3. 写入新的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        # 如果需要一行一个，用 \n 连接
        f.write("\n".join(us_lines))
        
    print(f"成功更新 {output_file}，共找到 {len(us_lines)} 条记录。")

except Exception as e:
    print(f"发生错误: {e}")