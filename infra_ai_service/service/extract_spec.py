#!/usr/bin/python3

import argparse
import os
import subprocess
import json
from tqdm import tqdm


def extract_spec_features():
    pass

if __name__ == '__main__':
    os_path_dict = {"centos": "/c/pkgmapping/centos/7.8.2003/", "opensuse": "/c/pkgmapping/opensuse/15.4/",
                    "openeuler": "/c/pkgmapping/openeuler/openEuler-22.03-LTS/", "fedora": "/c/pkgmapping/fedora/33/"}
    spec_json_dict = {"centos": "centos_7.8.2003_spec.json", "opensuse": "opensuse_15.4_spec.json",
                      "openeuler": "openeuler_openEuler-22.03-LTS_spec.json", "fedora": "fedora_33_spec.json"}

    parser = argparse.ArgumentParser(usage="""
                      提取centos、opensuse、openeuler和fedora源码包的spec文件特征
                 """)
    parser.add_argument('-o', type=str, required=True,
                        help="OS名称，可选填：centos|opensuse|openeuler|fedora")

    args = parser.parse_args()
    o = args.o

    os_path = os_path_dict[o]
    spec_json = spec_json_dict[o]
    folder_path = os_path + "repo/"

    data = {}
    count = 1

    # 遍历文件夹下的所有文件
    folder_list = os.listdir(folder_path)
    for folder in tqdm(folder_list):
        subfolder = os.path.join(folder_path, folder)
        if os.path.isdir(subfolder):
            # 遍历子文件夹下的所有文件
            flag = False
            for file in os.listdir(subfolder):
                if file.endswith('.spec'):
                    flag = True
                    break
            for file in os.listdir(subfolder):
                if not flag:
                    break
                if count not in data:
                    data[count] = {}

                if file.endswith('.spec'):
                    name = os.path.splitext(file)[0]
                    data[count]['name'] = name

                    output_binary = subprocess.run(['rpmspec', '-q', os.path.join(subfolder, file)],
                                                   cwd=subfolder, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    binary_list = output_binary.stdout.decode().strip().splitlines()
                    data[count]['binaryList'] = binary_list

                    output_providers = subprocess.run(['rpmspec', '-q', '--provides', os.path.join(subfolder, file)],
                                                      cwd=subfolder, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    provides = output_providers.stdout.decode().strip().splitlines()
                    new_provides = []
                    for p in provides:
                        if p.find('=') != -1:
                            new_provides.append(p.split('=')[0].strip())
                        else:
                            new_provides.append(p.strip())
                    data[count]['provides'] = new_provides

                    output_buildrequires = subprocess.run(
                        ['rpmspec', '-q', '--buildrequires', os.path.join(subfolder, file)],
                        cwd=subfolder, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    build_requires = output_buildrequires.stdout.decode().strip().splitlines()
                    new_build_requires = []
                    for br in build_requires:
                        if br.startswith('/'):
                            continue
                        if br.find('>=') != -1:
                            new_build_requires.append(br.split('>=')[0].strip())
                        elif br.find('>') != -1:
                            new_build_requires.append(br.split('>')[0].strip())
                        else:
                            new_build_requires.append(br.strip())
                    data[count]['buildRequires'] = new_build_requires

                    try:
                        source0_command = "rpmspec -P " + os.path.join(subfolder, file) + " | grep Source0:"
                        source_command = "rpmspec -P " + os.path.join(subfolder, file) + " | grep Source:"
                        if subprocess.getoutput(source0_command) != "":
                            source0 = subprocess.getoutput(source0_command).split("Source0:")[1].strip()
                        else:
                            source0 = subprocess.getoutput(source_command).split("Source:")[1].strip()
                        data[count]['source0'] = source0
                    except:
                        data[count]['source0'] = ""

                if file == 'src':
                    command_str_macro = "grep -E -Irho '\<[A-Z]+_[A-Z]+\>' '" + os.path.join(subfolder,
                                                                                             file) + "' | sort | uniq -c | sort -nr | head -10"
                    macro_str = subprocess.getoutput(command_str_macro)
                    if macro_str != '':
                        macro_list = macro_str.split('\n')
                        macre_names = []
                        # macro_counts = []
                        for macro in macro_list:
                            if macro.find("Permission denied") == -1:
                                macre_names.append(macro.strip().split(' ')[1])
                                # macro_counts.append(macro.strip().split(' ')[0])
                            else:
                                continue
                        data[count]['macro_names'] = macre_names
                        # data[count]['macro_counts'] = macro_counts
                    else:
                        data[count]['macro_names'] = []
                        # data[count]['macro_counts'] = []

                    command_str_email = "grep -E -Irho '\<[a-z]+@[a-z]+\.[a-z.]+\>' '" + os.path.join(subfolder,
                                                                                                      file) + "' | sort | uniq -c | sort -nr | head -10"
                    email_str = subprocess.getoutput(command_str_email)
                    if email_str != '':
                        email_list = email_str.split('\n')
                        email_names = []
                        # email_counts = []
                        for email in email_list:
                            if email.find("Permission denied") == -1:
                                email_names.append(email.strip().split(' ')[1])
                                # email_counts.append(email.strip().split(' ')[0])
                            else:
                                continue
                        data[count]['email_names'] = email_names
                        # data[count]['email_counts'] = email_counts
                    else:
                        data[count]['email_names'] = []
                        # data[count]['email_counts'] = []

                    command_str_class = "grep -rho '[A-Z][a-z]\{3,\}[A-Z][a-z]\{3,\}' '" + os.path.join(subfolder,
                                                                                                        file) + "' | sort | uniq -c | sort -nr | head -10"
                    class_str = subprocess.getoutput(command_str_class)
                    if class_str != '':
                        class_list = class_str.split('\n')
                        class_names = []
                        for c in class_list:
                            if c.find("Permission denied") == -1:
                                class_names.append(c.strip().split(' ')[1])
                            else:
                                continue
                        data[count]['class_names'] = class_names
                    else:
                        data[count]['class_names'] = []

                    command_str_path = "grep -E -Irho '\"/[A-Za-z.]+(/[A-Za-z.]+)*\"' '" + os.path.join(subfolder,
                                                                                                        file) + "' | sort | uniq -c | sort -nr | head -10"
                    path_str = subprocess.getoutput(command_str_path)
                    if path_str != '':
                        path_list = path_str.split('\n')
                        path_names = []
                        for path in path_list:
                            if path.find("Permission denied") == -1:
                                path_names.append(path.strip().split(' ')[1].replace('\"', ''))
                            else:
                                continue
                        data[count]['path_names'] = path_names
                    else:
                        data[count]['path_names'] = []

                    command_str_url = "grep -E -Irho '\"(https?|ftp)://([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(/.*)?\"' '" + os.path.join(
                        subfolder, file) + "' | sort | uniq -c | sort -nr | head -10"
                    url_str = subprocess.getoutput(command_str_url)
                    if url_str != '':
                        url_list = url_str.split('\n')
                        url_names = []
                        for url in url_list:
                            if url.find("Permission denied") == -1:
                                if url.strip().split(' ')[0].isdigit():
                                    url_name = url.strip().split(' ')[1]
                                    start = url_name.find('\"')
                                    end = url_name[start + 1:].find('\"')
                                    if start + end + 1 == len(url_name) - 1:
                                        if url_name.replace('\"', '') != "":
                                            url_names.append(url_name.replace('\"', ''))
                                    else:
                                        if url_name[1: start + end + 1] != "":
                                            url_names.append(url_name[1: start + end + 1])
                                else:
                                    continue
                            else:
                                continue
                        data[count]['url_names'] = url_names
                    else:
                        data[count]['url_names'] = []

            if flag:
                count += 1

    file_json = os_path + "json/" + spec_json
    folder_json = os.path.dirname(file_json)
    os.makedirs(folder_json, exist_ok=True)

    # 保存为 JSON 文件
    with open(file_json, 'w') as f:
        json.dump(data, f, indent=4)
