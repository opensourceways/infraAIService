import os
import gzip
import requests
import json

components = ['main', 'universe', 'multiverse', 'restricted']
base_url = 'http://archive.ubuntu.com/ubuntu'
api_url = 'http://0.0.0.0:8000/api/v1/feature-insert'

# 尝试从文件加载已处理的 dsc URLs，如果文件不存在则从空字典开始
try:
    with open('processed_dsc_urls.json', 'r') as f:
        processed_dsc_urls = json.load(f)
except FileNotFoundError:
    processed_dsc_urls = {}

for component in components:
    sources_url = f'{base_url}/dists/noble/{component}/source/Sources.gz'
    sources_gz = f'{component}_Sources.gz'
    os.system(f'wget -c {sources_url} -O {sources_gz}')

    with gzip.open(sources_gz, 'rt') as f:
        content = f.read()

    entries = content.strip().split('\n\n')
    for entry in entries:
        lines = entry.strip().split('\n')
        directory = ''
        for line in lines:
            if line.startswith('Directory: '):
                directory = line.split(' ')[1]
            elif line.startswith('Files:'):
                idx = lines.index(line) + 1
                while idx < len(lines) and lines[idx].startswith(' '):
                    parts = lines[idx].strip().split()
                    if len(parts) == 3 and parts[2].endswith('.dsc'):
                        dsc_file = parts[2]
                        dsc_url = f'{base_url}/{directory}/{dsc_file}'
                        package_name = dsc_file.split('_')[0]  # 获取包名
                        if dsc_url not in processed_dsc_urls:
                            payload = {
                                "src_rpm_url": "",
                                "src_deb_url": dsc_url,
                                "os_version": "ubuntu",
                                "package_name": package_name
                            }
                            response = requests.post(api_url, json=payload)
                            if response.status_code == 200:
                                processed_dsc_urls[dsc_url] = True  # 标记为已处理
                                with open('processed_dsc_urls.json',
                                          'w') as f:
                                    json.dump(processed_dsc_urls, f)
                            else:
                                print(
                                    f"Error posting data for {package_name}: {response.text}")
                    idx += 1
