import os
import socket
import time
import concurrent.futures

# ================= 配置项 =================
# 你想要批量处理的地区前缀列表（与你的 txt 文件名对应）
REGIONS = ["us", "jp", "sg", "hk", "tw", "kr", "uk", "de", "fr"]

TOP_N = 30                # 每个地区保留最快的前 30 个
TIMEOUT = 2.0             # 测试超时时间(秒)
MAX_THREADS = 50          # 并发线程数
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
    """处理单个地区的核心逻辑"""
    input_file = f"{region}.txt"
    output_file = f"{region}Res.txt"
    
    print(f"\n========== 开始处理 [{region.upper()}] 地区 ==========")
    
    if not os.path.exists(input_file):
        print(f"⏩ 找不到文件 '{input_file}'，自动跳过。")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_links = f.read().splitlines()
            
        raw_links = [link.strip() for link in raw_links if link.strip()]
        
        if not raw_links:
            print(f"⏩ '{input_file}' 是空文件，跳过。")
            return
            
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
                
                # 简单显示进度
                if completed % 100 == 0 or completed == len(raw_links):
                    print(f"   进度: {completed} / {len(raw_links)} ...")

        print(f"🔍 测速完成！找到 {len(results)} 个有效存活节点。")
        
        if len(results) == 0:
            print(f"❌ [{region.upper()}] 没有可连通的节点！")
            return

        # 排序并截取前 TOP_N
        results.sort(key=lambda x: x[0])
        top_nodes = results[:TOP_N]
        
        # 打印最快的前 3 个预览一下即可，避免刷屏太长
        print("⚡ 最快节点预览:")
        for i, (lat, link) in enumerate(top_nodes[:3]):
            print(f"   Top {i+1}: {lat:.0f} ms | {link}")
        if len(top_nodes) > 3:
            print(f"   ... (共保存 {len(top_nodes)} 个)")
            
        # 保存到本地文件
        top_links = [link for lat, link in top_nodes]
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(top_links))
            
        print(f"✅ 成功生成 '{output_file}'")

    except Exception as e:
        print(f"❌ 处理 [{region.upper()}] 时发生错误: {e}")

def main():
    print("🚀 开始批量测速任务...")
    start_total_time = time.time()
    
    # 循环遍历每一个地区进行处理
    for region in REGIONS:
        process_region(region)
        
    total_time = time.time() - start_total_time
    print(f"\n🎉 所有地区处理完毕！总耗时: {total_time:.1f} 秒。")
    print("现在你可以使用所有以 Res.txt 结尾的精选文件了！")

if __name__ == '__main__':
    main()