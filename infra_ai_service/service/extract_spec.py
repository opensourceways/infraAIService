#!/usr/bin/python3

import os
import subprocess
import copy
import urllib.request
import re
import tempfile
import uuid

from loguru import logger
from infra_ai_service.config.config import settings
from infra_ai_service.service.extract_xml import extract_xml_features
from infra_ai_service.service.utils import update_json

XML_INFO = None


def _download_from_url(url, file_path):
    try:
        urllib.request.urlretrieve(url, filename=file_path)
    except Exception as e:
        raise Exception(f"download file fail: {e}")


def _decompress_src_rpm(rpm_path):
    if not os.path.exists(rpm_path):
        raise Exception("check download rpm error, file not exit")

    cur_dir = os.path.dirname(rpm_path)
    try:
        rpm_dir = os.path.join(cur_dir, "tmp_src_rpm")
        cmd = ["rm", "-rf", rpm_dir]
        del_res = subprocess.run(cmd)
        if del_res.returncode != 0:
            raise ValueError(f"delete redundant dir fail: {del_res.stderr}")

        # rpm2cpio <pkg> | cpio -div -D <path>
        cmd = f"rpm2cpio {rpm_path} | cpio -div -D {rpm_dir}"
        res = subprocess.run(cmd, shell=True)
        if res.returncode != 0:
            raise ValueError(f"errcode[{res.stderr}]")
        return rpm_dir
    except Exception as e:
        raise Exception(f"decompress src.rpm fail: {e}")


def _get_tar_cmd(suffix, tar_path, dst_path):
    if not os.path.exists(tar_path):
        return None
    os.makedirs(dst_path)
    suffix_cmd = {
        ".tar.gz": f"tar -xzf {tar_path} -C {dst_path}",
        ".tgz": f"tar -xzf {tar_path} -C {dst_path}",
        ".tar.bz2": f"tar -xjf {tar_path} -C {dst_path}",
        ".tar.xz": f"tar -xJf {tar_path} -C {dst_path}",
        ".zip": f"unzip {tar_path} -d {dst_path}",
    }
    return suffix_cmd.get(suffix, None)


def _decompress_tar_file(rpm_dir):
    if not os.path.exists(rpm_dir):
        raise Exception("check decompress rpm error, directory not exit")

    suffix, tar_path = "", ""
    for file in os.listdir(rpm_dir):
        match = re.search(r"\.(tar\.gz|tar\.bz2|tar\.xz|zip|tgz)$", file)
        if match:
            suffix = match.group()
            tar_path = os.path.join(rpm_dir, file)
            break

    dst_path = os.path.join(rpm_dir, "src")
    cmd = _get_tar_cmd(suffix, tar_path, dst_path)
    if not cmd:
        raise ValueError("found new zip file")

    try:
        res = subprocess.run(cmd, shell=True)
        if res.returncode != 0:
            raise ValueError(f"returncode[{res.stderr}]")
        # TODO: maybe, don't need return
        return dst_path
    except Exception as e:
        raise Exception(f"decompress tar file error: {e}")


def process_src_rpm_from_url(url: str):
    if not url.endswith(".src.rpm"):
        raise Exception("url of src.rpm may be wrong")

    file_save_dir = os.path.expanduser(settings.SRC_RPM_DIR)

    if not os.path.exists(file_save_dir):
        os.makedirs(file_save_dir)

    # download .src.rpm file
    rpm_path = os.path.join(file_save_dir, "tmp.src.rpm")
    _download_from_url(url, rpm_path)

    # decompress .src.rpm file
    rpm_dir = _decompress_src_rpm(rpm_path)

    # decompress tar file
    _decompress_tar_file(rpm_dir)

    return rpm_dir


def _process_binarylist(binary_list, data_count):
    res = []
    for binary in binary_list:
        res.append(re.sub(r"-[0-9].*", "", binary))
    data_count["binaryList"] = res


def _process_provides(provides, data_count):
    new_provides = []
    for p in provides:
        if p.find("=") != -1:
            p = p.split("=")[0].strip()

        p = re.sub(r"\(x86-64\)", "", p).strip()
        p = re.sub(r"\(aarch-64\)", "", p).strip()
        p = re.sub(r"-debuginfo$", "", p).strip()
        p = re.sub(r"-debugsource$", "", p).strip()
        if p not in new_provides:
            new_provides.append(p)
    data_count["provides"] = new_provides


def _process_requires(build_requires, data_count):
    new_build_requires = []
    for br in build_requires:
        if br.startswith("/"):
            continue
        if br.find(">=") != -1:
            br = br.split(">=")[0].strip()
        elif br.find(">") != -1:
            br = br.split(">")[0].strip()

        br = re.sub(r"-devel$", "-dev", br)
        br = re.sub(r"-help$", "-doc", br)
        new_build_requires.append(br.strip())
    data_count["buildRequires"] = new_build_requires


def _process_source0(abs_path, data_count):
    try:
        source0_command = f"rpmspec -P {abs_path} | grep Source0:"
        source_command = f"rpmspec -P {abs_path} | grep Source:"
        if subprocess.getoutput(source0_command) != "":
            source0 = subprocess.getoutput(source0_command)
            source0 = source0.split("Source0:")[1].strip()
        else:
            source0 = subprocess.getoutput(source_command)
            source0 = source0.split("Source:")[1].strip()
        data_count["source0"] = source0
    except Exception:
        data_count["source0"] = ""


def _process_spec_file(dir_path: str, file: str, data: dict, count: int):
    if not data.get(count, None):
        data[count] = {}

    name = os.path.splitext(file)[0]
    data[count]["name"] = name
    try:
        abs_path = os.path.join(dir_path, file)
        cmd = ["rpmspec", "-q", abs_path]
        output_binary = subprocess.run(
            cmd, cwd=dir_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        cmd = ["rpmspec", "-q", "--provides", abs_path]
        output_providers = subprocess.run(
            cmd, cwd=dir_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        cmd = ["rpmspec", "-q", "--buildrequires", abs_path]
        output_buildrequires = subprocess.run(
            cmd, cwd=dir_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    except Exception as e:
        raise Exception(f"rpmspec cmd fail: {e}")

    binary_list = output_binary.stdout.decode().strip().splitlines()
    provides = output_providers.stdout.decode().strip().splitlines()
    build_requires = output_buildrequires.stdout.decode().strip().splitlines()

    _process_binarylist(binary_list, data[count])
    _process_provides(provides, data[count])
    _process_requires(build_requires, data[count])
    _process_source0(abs_path, data[count])


def _process_url_name(res: str):
    if res.strip().split(" ")[0].isdigit():
        url_name = res.strip().split(" ")[1]
        start = url_name.find('"')
        end = url_name[start + 1:].find('"')
        if start + end + 1 == len(url_name) - 1:
            return url_name.replace('"', "")
        else:
            return url_name[1: start + end + 1]
    return ""


def _process_src_dir_common(cmd, data_count):
    res_str = subprocess.getoutput(cmd[0])
    if res_str != "":
        res_list = res_str.split("\n")
        res_names = []
        for res in res_list:
            if res.find("Permission denied") == -1:
                if cmd[1] == "url_names":
                    url_name = _process_url_name(res)
                    if url_name != "":
                        res_names.append(url_name)
                elif cmd[1] == "path_names":
                    tmp_name = res.strip().split(" ")[1].replace('"', "")
                    res_names.append(tmp_name)
                else:
                    res_names.append(res.strip().split(" ")[1])
            else:
                continue
        data_count[cmd[1]] = res_names
    else:
        data_count[cmd[1]] = []


def _process_src_dir(src_path, data, count):
    if not data.get(count, None):
        data[count] = {}

    if not os.path.exists(src_path):
        raise Exception("src dir not exist")
    cmd_list = [
        (
            (
                "rg -o --no-filename "
                f"'\\<[A-Z]+_[A-Z]+\\>' '{src_path}' "
                "| sort | uniq -c | sort -nr | head -10"
            ),
            "macro_names",
        ),
        (
            (
                "rg -o --no-filename "
                f"'\\<[a-z]+@[a-z]+\\.[a-z.]+\\>' '{src_path}' "
                "| sort | uniq -c | sort -nr | head -10"
            ),
            "email_names",
        ),
        # class_names probably don't need -I para
        (
            (
                "rg -o --no-filename "
                f"'[A-Z][a-z]\\{{3,\\}}[A-Z][a-z]\\{{3,\\}}' '{src_path}'"
                " | sort | uniq -c | sort -nr | head -10"
            ),
            "class_names",
        ),
        (
            (
                "rg -o --no-filename "
                f"'\"/[A-Za-z.]+(/[A-Za-z.]+){{2,}}\"' '{src_path}' "
                "| sort | uniq -c | sort -nr | head -10"
            ),
            "path_names",
        ),
        (
            (
                "rg -o --no-filename "
                "'\"(https?|ftp)://([a-zA-Z0-9-]+.)+[a-zA-Z]{2,6}(/.*)?\"' "
                f"'{src_path}' | sort | uniq -c | sort -nr | head -10"
            ),
            "url_names",
        ),
    ]

    for cmd in cmd_list:
        _process_src_dir_common(cmd, data[count])


def decompress_xml_file(feature_xml_path: str):
    if feature_xml_path.endswith(".xml.zst"):
        cmd = ["zstd", "-d", feature_xml_path]
        dep_res = subprocess.run(cmd)

    if feature_xml_path.endswith(".xml.gz"):
        cmd = ["gzip", "-d", feature_xml_path]
        dep_res = subprocess.run(cmd)

    logger.info("decompress xml file finished")
    if dep_res.returncode != 0:
        raise ValueError(f"delete redundant dir fail: {dep_res.stderr}")


def check_xml_info(xml_url: str, os_version: str):
    """
    :param force_refresh: refresh xml feature info from xml file
    :type bool
    """
    with tempfile.TemporaryDirectory() as src_rpm_dir:
        if xml_url.endswith(".xml.zst"):
            base_name = f"{os_version}.xml.zst"
        if xml_url.endswith(".xml.gz"):
            base_name = f"{os_version}.xml.gz"

        feature_xml_path = os.path.join(src_rpm_dir, base_name)
        _download_from_url(xml_url, feature_xml_path)
        decompress_xml_file(feature_xml_path)

        feature_xml_path = feature_xml_path.replace(".zst", "")
        feature_xml_path = feature_xml_path.replace(".gz", "")

        if not os.path.exists(feature_xml_path):
            raise Exception("download xml unknown error")

        xml_info = extract_xml_features(feature_xml_path)
        xml_info.update({"os_version": os_version})

        return xml_info

    return None


def extract_spec_features(dir_path: str):
    if not XML_INFO:
        raise Exception('need to config xml with API "/feature-insert/xml/"')

    data = {}
    count = 1
    count_flag = 0
    for file in os.listdir(dir_path):
        if file.endswith(".spec"):
            _process_spec_file(dir_path, file, data, count)
            count_flag += 1

        if file == "src":
            src_path = os.path.join(dir_path, "src")
            _process_src_dir(src_path, data, count)
            count_flag += 1

        if count_flag == 2:
            count += 1
            count_flag = 0

    # os_version use only in API /feature-insert/
    # XML_INFO cann't change
    xml_info = copy.deepcopy(XML_INFO)
    if xml_info.get("os_version", None):
        del xml_info["os_version"]

    data = update_json(xml_info, data)

    return data


def process_src_deb_from_url(url: str):
    if not url.endswith(".dsc"):
        raise Exception("URL of .dsc may be wrong")

    file_save_all_dir = os.path.expanduser(settings.SRC_DEB_DIR)
    if not os.path.exists(file_save_all_dir):
        os.makedirs(file_save_all_dir)

    # download the .dsc file
    time_based_uuid = uuid.uuid1()
    file_save_dir = os.path.join(file_save_all_dir, time_based_uuid.__str__())
    if os.path.exists(file_save_dir):
        os.unlink(file_save_dir)
    os.makedirs(file_save_dir)
    dsc_path = os.path.join(file_save_dir, "tmp.dsc")

    _download_from_url(url, dsc_path)

    cmd = [
        "chroot", "/mnt/debian", "bash", "-c",
        f"cd /root/{time_based_uuid.__str__()} && dget -u {url}"
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise Exception(f"dget failed: {res.stderr}")
        print(
            f"Source package downloaded and extracted successfully to "
            f"{file_save_dir}")
    except Exception as e:
        raise Exception(
            f"Error occurred while downloading source package: {e}")

    return file_save_dir


def dealing_with_dsc_content(dir_path: str):
    # Find the .dsc file in the dir_path
    dsc_file = None
    for file in os.listdir(dir_path):
        if file.endswith(".dsc"):
            dsc_file = os.path.join(dir_path, file)
            break
    if not dsc_file:
        raise Exception("No .dsc file found in source directory")

    # Parse the .dsc file
    with open(dsc_file, 'r') as f:
        dsc_content = f.read()

    fields = {
        "Source": "",
        "Binary": "",
        "Version": "",
        "Homepage": "",
        "Build-Depends": "",
        "Package-List": ""
    }

    for field in fields:
        start_index = dsc_content.find(field + ":")
        if start_index != -1:
            if field == "Package-List":
                start_index += len(field) + 1
                end_index = dsc_content.find("Checksums", start_index)
                if end_index == -1:
                    end_index = len(dsc_content)
                fields[field] = dsc_content[start_index:end_index].strip()
            else:
                start_index += len(field) + 1
                end_index = dsc_content.find("\n", start_index)
                fields[field] = dsc_content[start_index:end_index].strip()

    # Format the fields into the desired data structure
    data_count = format_fields(fields)
    for index in range(len(data_count["binaryList"])):
        data_count["binaryList"][index] = data_count["binaryList"][
            index].replace(',', '').strip()
    for index in range(len(data_count["requires"])):
        data_count["requires"][index] = data_count["requires"][index].strip()
        if data_count["requires"][index].find('(') != -1:
            data_count["requires"][index] = \
                data_count["requires"][index].split('(')[0].strip()
    for index in range(len(data_count["provides"])):
        data_count["provides"][index] = \
            data_count["provides"][index].strip().split(' ')[0]

    return data_count


def dealing_with_src_macro_name(src_dir, data_count):
    # macro_names
    cmd_macro = "grep -E -Irho '\\<[A-Z]+_[A-Z]+\\>' '" + src_dir + (
        "' | sort | uniq -c | sort -nr | head -10")
    macro_str = subprocess.getoutput(cmd_macro)
    macro_names = []
    if macro_str:
        for line in macro_str.strip().split('\n'):
            if "Permission denied" not in line:
                macro_names.append(line.strip().split()[-1])
    data_count['macro_names'] = macro_names


def dealing_with_src_email_names(src_dir, data_count):
    # email_names
    cmd_email = ("grep -E -Irho '\\<[a-z]+@[a-z]+\\.[a-z.]+\\>' '" + src_dir
                 + "' | sort | uniq -c | sort -nr | head -10")
    email_str = subprocess.getoutput(cmd_email)
    email_names = []
    if email_str:
        for line in email_str.strip().split('\n'):
            if "Permission denied" not in line:
                email_names.append(line.strip().split()[-1])
    data_count['email_names'] = email_names


def dealing_with_src_class_names(src_dir, data_count):
    # class_names
    cmd_class = ("grep -rho '[A-Z][a-z]\\{3,\\}[A-Z][a-z]\\{3,\\}' '" +
                 src_dir
                 + "' | sort | uniq -c | sort -nr | head -10")
    class_str = subprocess.getoutput(cmd_class)
    class_names = []
    if class_str:
        for line in class_str.strip().split('\n'):
            if "Permission denied" not in line:
                class_names.append(line.strip().split()[-1])
    data_count['class_names'] = class_names


def dealing_with_src_path_names(src_dir, data_count):
    # path_names
    cmd_path = ("grep -E -Irho '\"/[A-Za-z\\.]+(/[A-Za-z\\.]+)*\"' '" +
                src_dir + "' | sort | uniq -c | sort -nr | head -10")
    path_str = subprocess.getoutput(cmd_path)
    path_names = []
    if path_str:
        for line in path_str.strip().split('\n'):
            if "Permission denied" not in line:
                path = line.strip().split()[-1].replace('"', '')
                path_names.append(path)
    data_count['path_names'] = path_names


def dealing_with_src_url_names(src_dir, data_count):
    # url_names
    cmd_url = (("grep -E -Irho '\"(https?|ftp)://([a-zA-Z0-9-]+\\.)+[a-zA-Z]{"
                "2,6}(/.*)?\"' '") +
               src_dir + "' | sort | uniq -c | sort -nr | head -10")
    url_str = subprocess.getoutput(cmd_url)
    url_names = []
    if url_str:
        for line in url_str.strip().split('\n'):
            if "Permission denied" not in line:
                if line.strip().split(' ')[0].isdigit():
                    url_name = line.strip().split(' ')[1]
                    if url_name.endswith('\"') is False:
                        url_name += '\"'
                    start = url_name.find('\"')
                    end = url_name[start + 1:].find('\"')
                    if start + end + 1 == len(url_name) - 1:
                        if url_name.replace('\"', '') != "":
                            url_names.append(url_name.replace('\"', ''))
                    else:
                        if url_name[1: start + end + 1] != "":
                            url_names.append(url_name[1: start + end + 1])
    data_count['url_names'] = url_names


def extract_dsc_features(dir_path: str):
    if not os.path.exists(dir_path):
        raise Exception("Source directory does not exist")

    data_count = dealing_with_dsc_content(dir_path)

    src_dir = dir_path

    dealing_with_src_macro_name(src_dir, data_count)

    dealing_with_src_email_names(src_dir, data_count)

    dealing_with_src_class_names(src_dir, data_count)

    dealing_with_src_path_names(src_dir, data_count)

    dealing_with_src_url_names(src_dir, data_count)

    return data_count


def format_fields(fields):
    formatted_fields = {
        "name": fields.get("Source", ""),
        "binaryList": fields.get("Binary", "").replace(',', '').split(),
        "version": fields.get("Version", ""),
        "url": fields.get("Homepage", ""),
        "requires": [req.strip().split('(')[0].strip() for req in
                     fields.get("Build-Depends", "").split(",")],
        "provides": [line.strip().split(' ')[0] for line in
                     fields.get("Package-List", "").split("\n") if
                     line.strip()],
        "description": "",
        "summary": "",
        "buildRequires": [],
        "source0": ""
    }
    return formatted_fields
