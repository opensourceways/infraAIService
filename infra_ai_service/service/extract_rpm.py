#!/usr/bin/python3

import argparse
import os
import xml.etree.ElementTree as ET
import json


def strip_namespace(tag_name):
    return tag_name.split('}')[-1]


def process_xml_file(file_path):
    firstLevel = ET.parse(file_path, parser=ET.XMLParser(encoding='utf-8')).getroot()
    data = {}
    count = 1
    for secondLevel in firstLevel:
        if strip_namespace(secondLevel.tag) != 'package':
            continue

        if len(secondLevel) == 0:
            data[count] = secondLevel.text.strip() if secondLevel.text else ''
        else:
            data[count] = {}
            for thirdLevel in secondLevel:
                if strip_namespace(thirdLevel.tag) == 'name':
                    data[count][strip_namespace(thirdLevel.tag)] = thirdLevel.text if thirdLevel.text else ''
                elif strip_namespace(thirdLevel.tag) == 'version':
                    data[count][strip_namespace(thirdLevel.tag)] = thirdLevel.get('ver').strip() if thirdLevel.get(
                        'ver') else ''
                elif strip_namespace(thirdLevel.tag) == 'summary':
                    data[count][strip_namespace(thirdLevel.tag)] = thirdLevel.text.strip() if thirdLevel.text else ''
                elif strip_namespace(thirdLevel.tag) == 'description':
                    data[count][strip_namespace(thirdLevel.tag)] = thirdLevel.text.strip() if thirdLevel.text else ''
                elif strip_namespace(thirdLevel.tag) == 'url':
                    data[count][strip_namespace(thirdLevel.tag)] = thirdLevel.text.strip() if thirdLevel.text else ''
                elif strip_namespace(thirdLevel.tag) == 'format':
                    for fourthLevel in thirdLevel:
                        if strip_namespace(fourthLevel.tag) == 'requires':
                            data[count]['requires'] = [r.get('name') for r in
                                                       fourthLevel.findall('{http://linux.duke.edu/metadata/rpm}entry')]

            # 处理特殊情况
            version = data[count]['version']
            if version.rfind('.') != -1:
                data[count]['version'] = version[0: version.rfind('.')]

            if data[count]['description'] == '.':
                data[count]['description'] = ""

            if 'requires' in data[count]:
                requires = data[count]['requires']
                new_requires = []
                for r in requires:
                    if r.startswith('/'):
                        continue
                    if r.find('>=') != -1:
                        new_requires.append(r.split('>=')[0].strip())
                    elif r.find('>') != -1:
                        new_requires.append(r.split('>')[0].strip())
                    else:
                        new_requires.append(r.strip())
                data[count]['requires'] = new_requires
            else:
                data[count]['requires'] = []
        count += 1
    return data


def read_xml_files(folder):
    xml_files = []
    for file in os.listdir(folder):
        if file.endswith('.xml'):
            xml_files.append(os.path.join(folder, file))

    all_data = {}
    for xml_file in xml_files:
        file_name = os.path.basename(xml_file)
        data = process_xml_file(xml_file)
        all_data[file_name] = data

    return all_data

def extract_rpm_features():
    pass

if __name__ == '__main__':
    os_path_dict = {"centos": "/c/pkgmapping/centos/7.8.2003/", "opensuse": "/c/pkgmapping/opensuse/15.4/",
                    "openeuler": "/c/pkgmapping/openeuler/openEuler-22.03-LTS/", "fedora": "/c/pkgmapping/fedora/33/"}
    rpm_json_dict = {"centos": "centos_7.8.2003_rpm.json", "opensuse": "opensuse_15.4_rpm.json",
                     "openeuler": "openeuler_openEuler-22.03-LTS_rpm.json", "fedora": "fedora_33_rpm.json"}

    parser = argparse.ArgumentParser(usage="""
                      提取centos、opensuse、openeuler和fedora源码包的rpm文件特征
                 """)
    parser.add_argument('-o', type=str, required=True,
                        help="OS名称，可选填：centos|opensuse|openeuler|fedora")

    args = parser.parse_args()
    o = args.o
    os_path = os_path_dict[o]
    rpm_json = rpm_json_dict[o]

    # 调用函数读取所有 XML 文件
    xml_data = read_xml_files(os_path + "rpmxml")
    file_json = os_path + "json/" + rpm_json

    folder_json = os.path.dirname(file_json)
    os.makedirs(folder_json, exist_ok=True)

    # 保存为 JSON 文件
    with open(file_json, 'w') as f:
        json.dump(xml_data, f, indent=4)
