#!/usr/bin/python3
import re
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger


from infra_ai_service.service.embedding_service import create_embedding
from infra_ai_service.service.utils import convert_to_str
from infra_ai_service.service.extract_spec import (
    process_src_rpm_from_url,
    extract_spec_features,
    check_xml_info,
)

import infra_ai_service.service.extract_spec as es

router = APIRouter()


class FeatureInsertRequest(BaseModel):
    src_rpm_url: str
    os_version: str
    package_name: str = ""


class FeatureInsertXml(BaseModel):
    xml_url: str
    os_version: str
    force_refresh: bool = False


@router.post("/")
async def feature_insert(request: FeatureInsertRequest = Body(...)):
    try:
        if not es.XML_INFO:
            raise Exception("need config xml with API '/feature-insert/xml/'")

        xml_version = es.XML_INFO.get("os_version", "%v!@#")  # foolproof
        if xml_version != request.os_version:
            raise Exception(
                "xml os version conflict, please config xml again,"
                f"{xml_version}:{request.os_version}"
            )

        # download and decompress .src.rpm file
        rpm_decompress_dir = process_src_rpm_from_url(request.src_rpm_url)
        logger.info(
            f"process src rpm finished rpm_decompress_dir:{rpm_decompress_dir}"
        )
        feature = extract_spec_features(
            rpm_decompress_dir,
        )
        logger.info(f"extrac spec features finished feature:{feature}")
        name = feature[1]["name"]
        if name != request.package_name:
            logger.debug(f"name difference {name}: {request.package_name}")

        name = request.package_name if request.package_name else name

        ordered_feature = convert_to_str(feature[1])
        feature_str = re.sub(r"[{}[\]()@#.\':\/-]", "", str(ordered_feature))
        logger.info(f"feature_str build finished:{feature_str}")
        create_embedding(feature_str, request.os_version, name)

        resp_data = {
            "status": "success",
            "insert_content": f"{ordered_feature}",
        }
        return JSONResponse(content=resp_data)
    except Exception as e:
        resp_data = {"status": "error", "message": str(e)}
        return JSONResponse(content=resp_data)


@router.post("/xml/")
def config_xml(request: FeatureInsertXml = Body(...)):
    try:
        if not request.force_refresh and es.XML_INFO is not None:
            latest_version = es.XML_INFO.get("os_version", None)
            if latest_version == request.os_version:
                raise Exception(
                    f"already config os_version[{latest_version}],"
                    "need to config with 'force_refresh'=True"
                )

        es.XML_INFO = check_xml_info(request.xml_url, request.os_version)
        resp_data = {
            "status": "success",
        }
        return JSONResponse(content=resp_data)
    except Exception as e:
        resp_data = {"status": "error", "message": str(e)}
        return JSONResponse(content=resp_data)
