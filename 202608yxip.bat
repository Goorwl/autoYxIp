@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"
title Cloudflare IP 本地聚合优选测速工具

echo ========================================================
echo 0. 正在检查测速组件...
echo ========================================================

if not exist "CloudflareST.exe" (
    echo 未检测到 CloudflareST.exe，正在自动从 Github 下载测速引擎，请稍候...
    powershell -NoProfile -Command ^
        "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
        "$url = 'https://ghproxy.net/https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.5/CloudflareST_windows_amd64.zip';" ^
        "try { Invoke-WebRequest -Uri $url -OutFile 'CFST.zip' -UseBasicParsing } catch { " ^
        "   $url = 'https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.5/CloudflareST_windows_amd64.zip';" ^
        "   Invoke-WebRequest -Uri $url -OutFile 'CFST.zip' -UseBasicParsing " ^
        "};" ^
        "Expand-Archive -Path 'CFST.zip' -DestinationPath '.' -Force;" ^
        "Remove-Item 'CFST.zip' -Force -ErrorAction SilentlyContinue;"
    
    if not exist "CloudflareST.exe" (
        echo [错误] 自动下载失败，请手动下载 CloudflareST.exe 并放到本脚本同一目录下！
        echo 下载地址: https://github.com/XIU2/CloudflareSpeedTest/releases
        pause
        exit /b
    )
    echo 测速组件部署成功！
)

echo.
echo ========================================================
echo 1. 正在从多个远程源下载并合并 IP 数据...
echo ========================================================

:: 在此处添加你的所有网址列表，用双引号包裹，以空格分隔
set "URLS=https://bestcf.pages.dev/s5gy/hk.txt https://bestcf.pages.dev/domain/all.txt https://bestcf.pages.dev/vps789/top100.txt https://bestcf.pages.dev/domain/ygkkk/all.txt https://bestcf.pages.dev/domain/qms/all.txt https://bestcf.pages.dev/domain/senflare/all.txt https://bestcf.pages.dev/domain/wuya/all.txt https://bestcf.pages.dev/domain/wuya/all.txt https://bestcf.pages.dev/domain/ircf/all.txt https://bestcf.pages.dev/wetest/ipv4.txt https://bestcf.pages.dev/uouin/all.txt https://bestcf.pages.dev/xinyitang3/ipv4.txt https://bestcf.pages.dev/luoli/all.txt https://bestcf.pages.dev/cfyes/ipv4.txt https://bestcf.pages.dev/tiancheng/all.txt https://bestcf.pages.dev/s5gy/all.txt https://bestcf.pages.dev/gslege/Cfxyz.txt https://cf.junzhen.qzz.io/best_ips_bj.txt https://cf.junzhen.qzz.io/best_ips.txt https://raw.githubusercontent.com/love-ztm/cfip/refs/heads/main/best_ips.txt https://raw.githubusercontent.com/svip-s/cloudflare_ip/refs/heads/main/best_ips.txt https://raw.githubusercontent.com/love-ztm/cfip/refs/heads/main/ubest_ips.txt https://bestcf.pages.dev/zhixuanwang/ipv4-onlyip.txt https://bestcf.pages.dev/vvhan/ipv4.txt https://bestcf.pages.dev/nirevil/ipv4.txt https://raw.githubusercontent.com/ymyuuu/IPDB/refs/heads/main/BestCF/bestcfv4.txt https://raw.githubusercontent.com/yuanxiawan/cfipv4db/refs/heads/main/cfip.txt https://bestcf.pages.dev/cmliu/all.txt https://bestcf.pages.dev/lzj/all.txt https://bestcf.pages.dev/lajiao/all.txt https://bestcf.pages.dev/moistr/all.txt https://bestcf.pages.dev/kristi/all.txt https://raw.githubusercontent.com/LancelotRar/best-cf-ips/refs/heads/main/best-cf-ipv4.txt https://raw.githubusercontent.com/JieChaoCC/cf-ip-auto/refs/heads/main/data/ipapi.txt https://raw.githubusercontent.com/ahang39/router/refs/heads/main/all.txt https://bestcf.pages.dev/ircf/ipv4.txt https://raw.githubusercontent.com/einsitang/my-fast-cf-ip/refs/heads/master/fastips.txt  https://raw.githubusercontent.com/hubbylei/bestcf/refs/heads/main/bestcf.txt https://bestcf.pages.dev/yutian/all.txt https://raw.githubusercontent.com/gshtwy/CF-DNS-Clone/refs/heads/main/wetest-cloudflare-v4.txt https://warp-masque-bestip.pages.dev/?ips=50&level=all&port=random  https://warp-masque-bestip.pages.dev/?ips=50&level=p0&port=random https://090227.pages.dev/bestcf?isp=all&ips=20 https://randomip.pages.dev/?c=all&n=50&p=random https://bestcf.pages.dev/random-region/US/100.txt https://bestcf.pages.dev/random-region/JP/100.txt https://bestcf.pages.dev/random-region/KR/50.txt https://bestcf.pages.dev/random-region/HK/100.txt https://bestcf.pages.dev/random-region/SG/100.txt"

powershell -NoProfile -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
    "$urls = '%URLS%'.Split(' ', [StringSplitOptions]::RemoveEmptyEntries);" ^
    "$allLines = [System.Collections.Generic.List[string]]::new();" ^
    "foreach($url in $urls){" ^
    "   try {" ^
    "       $res = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 10 -UserAgent 'Mozilla/5.0';" ^
    "       $allLines.AddRange($res.Split(\"`r`n\", [StringSplitOptions]::RemoveEmptyEntries));" ^
    "   } catch { Write-Host \"[跳过] 下载失败: $url\" -ForegroundColor Yellow }" ^
    "}" ^
    "$dict = [System.Collections.Generic.Dictionary[string, string]]::new();" ^
    "$ipList = [System.Collections.Generic.List[string]]::new();" ^
    "foreach($line in $allLines){" ^
    "   $line = $line.Trim().Trim([char]65279);" ^
    "   if($line -match '^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d+))?(.*)$'){" ^
    "       $ip = $matches[1];" ^
    "       $port = if($matches[2]) { $matches[2] } else { '443' };" ^
    "       $key = \"$ip`:$port\";" ^
    "       if(-not $dict.ContainsKey($key)){" ^
    "           $dict.Add($key, $line);" ^
    "           if(-not $ipList.Contains($ip)) { $ipList.Add($ip) }" ^
    "       }" ^
    "   }" ^
    "}" ^
    "[System.IO.File]::WriteAllLines('ip_for_test.txt', $ipList, (New-Object System.Text.UTF8Encoding($false)));" ^
    "$mapLines = [System.Collections.Generic.List[string]]::new();" ^
    "foreach($pair in $dict){ $mapLines.Add(\"$($pair.Key)=$($pair.Value)\") };" ^
    "[System.IO.File]::WriteAllLines('ip_mapping.tmp', $mapLines, (New-Object System.Text.UTF8Encoding($false)));" ^
    "Write-Host \"成功汇总并去重，共计获取到 $($ipList.Count) 个独立 IP 待测。\" -ForegroundColor Green;"

if not exist ip_for_test.txt (
    echo [错误] 未获取到任何 IP 数据，请检查网络或 URL 链接！
    pause
    exit /b
)

echo.
echo ========================================================
echo 2. 开始本地测速 (测试延迟与丢包，选取前 100 个最优节点)...
echo ========================================================

:: -f 传入纯 IP 文件
:: -tp 指定测速端口为 443
:: -dd 禁用下载测速，测速极快
:: -p 输出前 100 个
.\CloudflareST.exe -f ip_for_test.txt -tp 443 -dd -p 100 -o result.csv

if not exist result.csv (
    echo [错误] 测速未生成结果文件！
    pause
    exit /b
)

echo.
echo ========================================================
echo 3. 正在生成最终优选结果到 0260820yxip.txt ...
echo ========================================================

powershell -NoProfile -Command ^
    "$map = @{};" ^
    "Get-Content 'ip_mapping.tmp' -Encoding UTF8 | ForEach-Object {" ^
    "   $parts = $_ -split '=', 2;" ^
    "   if($parts.Count -eq 2){ $map[$parts[0]] = $parts[1] }" ^
    "};" ^
    "$finalList = [System.Collections.Generic.List[string]]::new();" ^
    "Import-Csv -Path 'result.csv' | Select-Object -First 50 | ForEach-Object {" ^
    "   $ip = $_.'IP 地址';" ^
    "   if(-not $ip){ $ip = $_.IP }" ^
    "   $matched = $false;" ^
    "   foreach($k in $map.Keys){" ^
    "       if($k.StartsWith(\"$ip`:\")){" ^
    "           $finalList.Add($map[$k]);" ^
    "           $matched = $true;" ^
    "           break;" ^
    "       }" ^
    "   }" ^
    "   if(-not $matched){ $finalList.Add(\"$ip`:443#优选延迟\") }" ^
    "};" ^
    "[System.IO.File]::WriteAllLines('0260820yxip.txt', $finalList, (New-Object System.Text.UTF8Encoding($false)));"

:: 清理过程产生的临时文件
del /f /q ip_for_test.txt ip_mapping.tmp result.csv >nul 2>&1

echo.
echo [大功告成] 最优 100 个节点已保存到：0260820yxip.txt
echo ========================================================
type 0260820yxip.txt
echo ========================================================
pause