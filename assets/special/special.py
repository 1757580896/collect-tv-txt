import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone

# 读取文本方法
def read_txt_to_array(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    except FileNotFoundError:
        print(f"文件 '{file_name}' 未找到。")
        return []
    except Exception as e:
        print(f"发生错误: {e}")
        return []

all_lines = []
# 读取排除列表
excudelist_lines = read_txt_to_array('assets/special/ExcludeList.txt') 

def convert_m3u_to_txt(m3u_content):
    """
    将多行M3U格式转换为"频道名称,URL"格式
    """
    txt_lines = []
    current_channel = ""
    
    for line in m3u_content:
        line = line.strip()
        if line.startswith("#EXTINF"):
            # 提取频道名称(最后一个逗号后的内容)
            parts = line.split(',')
            if len(parts) > 1:
                current_channel = parts[-1].strip()
        elif line.startswith(("http://", "https://", "rtmp://", "p3p://", "p2p://")):
            if current_channel:
                # 检查是否是有效的URL
                if any(proto in line for proto in ["http://", "https://", "rtmp://"]):
                    txt_lines.append(f"{current_channel},{line}")
                current_channel = ""  # 重置当前频道
    
    return "\n".join(txt_lines)

def process_url(url):
    try:
        # 创建请求对象并添加自定义header
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')

        # 打开URL并读取内容
        with urllib.request.urlopen(req) as response:
            data = response.read()
            text = data.decode('utf-8')
            lines = text.splitlines()  # 使用splitlines()更好处理不同换行符

            # 检查是否是M3U格式
            if lines and lines[0].strip().startswith("#EXTM3U"):
                print("检测到M3U格式，开始转换...")
                converted = convert_m3u_to_txt(lines)
                lines = converted.split('\n') if converted else []
                print(f"转换后行数: {len(lines)}")

            # 处理每一行
            for line in lines:
                line = line.strip()
                if (line and "#genre#" not in line 
                    and "," in line 
                    and any(proto in line for proto in ["http://", "https://"])
                    and line not in excudelist_lines):
                    all_lines.append(line)

    except Exception as e:
        print(f"处理URL时发生错误：{e}")

# 定义要处理的URL列表
urls = [
    "https://ua.fongmi.eu.org/box.php?url=https://xn--dkw0c.v.nxog.top/m/tv",
    "https://ua.fongmi.eu.org/box.php?url=https://py.nxog.top/zm/api/jm/api.php?ou=https://xn--dkw0c.v.nxog.top/m/tv/1",
    "https://ua.fongmi.eu.org/box.php?url=http://%E6%88%91%E4%B8%8D%E6%98%AF.%E6%91%B8%E9%B1%BC%E5%84%BF.com/live.php",
    "https://ua.fongmi.eu.org/box.php?url=http://sinopacifichk.com/tv/live",
    "https://ua.fongmi.eu.org/box.php?url=https://tv.iill.top/m3u/Gather",
]

# 处理每个URL
for url in urls:
    if url.startswith("http"):        
        print(f"\n正在处理URL: {url}")
        process_url(url)

# 将结果写入文件
output_file = "assets/special/special.txt"

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_lines))
    print(f"\n成功保存 {len(all_lines)} 条结果到文件: {output_file}")
    print("示例结果:")
    for line in all_lines[:5]:  # 打印前5行作为示例
        print(line)

except Exception as e:
    print(f"保存文件时发生错误：{e}")
