import os
import socket
import time
import concurrent.futures

# ================= 配置项 =================
REGIONS = ["us", "jp", "sg", "hk", "tw", "kr", "uk", "de", "fr"]

TOP_N = 30                # 每个单独地区文件保留最快的前 30 个
SUMMARY_TOP_N = 10        # 汇总文件(allRes)中每个地区保留前 10 个
TIMEOUT = 2.0             # 测试超时时间(秒)
MAX_THREADS = 50          # 并发线程数

ALL_RES_FILE = "allRes.txt" # 最终汇总的文件名
# ==========================================

def extract_host_port(link):
    """提取 IP 和 端口"""
    try:
        clean_link = link.split('#')[0].strip()
        if ':' in clean_link:
            host, port_str = clean_link.rsplit(':', 1)
            if port_str.isdigit():
                return host.strip(), int(port_str)
    except Exception:
        pass
    return None, None

def tcp_ping(host, port):
    """执行 TCP Ping"""
    try:
        start_time = time.time()
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return (time.time() - start_time) * 1000
    except Exception:
        return float('inf')

def test_node(link):
    """测试单个节点"""
    link = link.strip()
    if not link:
        return float('inf'), link
        
    host, port = extract_host_port(link)
    if not host or not port:
        return float('inf'), link
        
    latency = tcp_ping(host, port)
    return latency, link

def process_region(region):
    """处理单个地区，并返回该地区所有存活节点的列表"""
    input_file = f"{region}.txt"
    output_file = f"{region}Res.txt"
    
    print(f"\n========== 开始处理 [{region.upper()}] 地区 ==========")
    
    if not os.path.exists(input_file):
        print(f"⏩ 找不到文件 '{input_file}'，自动跳过。")
        return []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_links = f.read().splitlines()
            
        raw_links = [link.strip() for link in raw_links if link.strip()]
        
        if not raw_links:
            print(f"⏩ '{input_file}' 是空文件，跳过。")
            return []
            
        print(f"📥 读取到 {len(raw_links)} 个节点，开始多线程测速...")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_link = {executor.submit(test_node, link): link for link in raw_links}
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_link):
                latency, link = future.result()
                if latency != float('inf'):
                    results.append((latency, link))
                completed += 1
                
                if completed % 100 == 0 or completed == len(raw_links):
                    print(f"   进度: {completed} / {len(raw_links)} ...")

        print(f"🔍 测速完成！找到 {len(results)} 个有效存活节点。")
        
        if len(results) == 0:
            print(f"❌ [{region.upper()}] 没有可连通的节点！")
            return []

        results.sort(key=lambda x: x[0])
        top_nodes = results[:TOP_N]
        
        print("⚡ 最快节点预览:")
        for i, (lat, link) in enumerate(top_nodes[:3]):
            print(f"   Top {i+1}: {lat:.0f} ms | {link}")
        if len(top_nodes) > 3:
            print(f"   ... (共保存 {len(top_nodes)} 个)")
            
        top_links = [link for lat, link in top_nodes]
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(top_links))
            
        print(f"✅ 成功生成 '{output_file}'")
        return top_links

    except Exception as e:
        print(f"❌ 处理 [{region.upper()}] 时发生错误: {e}")
        return []

def main():
    print("🚀 开始批量测速任务...")
    start_total_time = time.time()
    
    all_res_lines = []
    
    for region in REGIONS:
        top_links = process_region(region)
        
        if top_links:
            # 1. 截取该地区的前 10 个
            top_10 = top_links[:SUMMARY_TOP_N]
            
            # 2. 去掉每个节点后面的 # 备注（例如把 "1.1.1.1:443#US" 变成 "1.1.1.1:443"）
            clean_top_10 = [link.split('#')[0].strip() for link in top_10]
            
            # 3. 用逗号将纯净的 IP:端口 连接起来
            merged_links = ",".join(clean_top_10)
            
            # 4. 在最前面加上 "US: " 这种地区前缀
            formatted_line = f"{region.upper()}: {merged_links}"
            
            # 5. 添加到汇总列表
            all_res_lines.append(formatted_line)
            
    if all_res_lines:
        print("\n📝 正在生成全地区精华版汇总文件...")
        with open(ALL_RES_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(all_res_lines))
        print(f"🌟 汇总成功！已生成 '{ALL_RES_FILE}' (共包含 {len(all_res_lines)} 个地区的优质节点)")
    else:
        print("\n⚠️ 没有任何存活节点，无法生成汇总文件。")
        
    total_time = time.time() - start_total_time
    print(f"\n🎉 所有任务处理完毕！总耗时: {total_time:.1f} 秒。")

if __name__ == '__main__':
    main()