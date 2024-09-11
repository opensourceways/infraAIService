import os
import re
import json
from openai import OpenAI
from .utils import (
    gen_func_description,
    repair_spec,
    repair_spec_pro,
    repair_spec_impl,
    get_patch,
    save_log,
)

SYSTEM_PROMPT = "你是一位经验丰富RPM软件包构建人员，你的任务是根据提供的spec脚本和报错日志修复spec脚本，以解决构建过程中出现的问题。"

PROMPT_TEMPLATE = """
spec脚本：
{spec}

报错日志：
{log}
"""

SYSTEM_PROMPT_PRO = """
## 任务：根据提供的spec脚本、报错日志定位问题，并通过项目文档给出修改建议，给出的代码中附带行号

## 输入格式：

spec脚本：
<spec脚本>

报错日志：
<报错日志>

项目文档：
<项目文档>

## 输出格式：

问题定位：
<问题定位>

修改建议：
<修改建议>

"""

PROMPT_TEMPLATE_PRO_1 = """
spec脚本：
{spec}

报错日志：
{log}

项目文档：
{doc}
"""

PROMPT_TEMPLATE_PRO_2 = """
## 任务：请根据提供的spec脚本、问题定位和修改建议修复spec脚本，以解决构建过程中出现的问题。如果不是由spec脚本引起的错误，请忽略。

{info}

spec脚本：
{spec}
"""


class SpecBot:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", None)
        base_url = os.getenv("OPENAI_BASE_URL", None)
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = "gpt-4-0613"

    def repair(self, input_spec, input_log, output_spec, output_log):
        spec = self._preprocess_spec(input_spec)
        log = self._preprocess_log(input_log)
        tools = self._prepare_tools()
        messages = self._prepare_messages(spec, log)
        fault_segment = None
        repaired_segment = None

        is_repaired = False
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "repair_spec"}},
            )
            tool_calls = response.choices[0].message.tool_calls
            arguments = tool_calls[0].function.arguments
            arguments = json.loads(arguments)
            suggestion = arguments.get("suggestion", None)
            fault_segment = arguments.get("fault_segment", None)
            repaired_segment = arguments.get("repaired_segment", None)

            if suggestion and fault_segment and repaired_segment:
                is_repaired = repair_spec_impl(
                    input_spec, fault_segment, repaired_segment, output_spec
                )
        except Exception as e:
            suggestion = str(e)

        patch = get_patch(input_spec, output_spec) if is_repaired else None
        save_log(output_log, is_repaired, log, suggestion, fault_segment, patch)

        return suggestion, is_repaired

    def repair_pro(self, input_spec, input_log, input_doc, output_spec, output_log):
        spec = self._preprocess_spec(input_spec)
        log = self._preprocess_log(input_log)
        doc = self._prepare_doc(input_doc)
        tools = self._prepare_tools_pro()
        fault_segment = None
        repaired_segment = None

        is_repaired = False
        try:
            messages = self._prepare_messages_pro_1(spec, log, doc)
            response = self.client.chat.completions.create(
                model="claude-3-5-sonnet-20240620", messages=messages
            )
            suggestion = response.choices[0].message.content

            messages = self._prepare_messages_pro_2(spec, suggestion, doc)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice={
                    "type": "function",
                    "function": {"name": "repair_spec_pro"},
                },
            )
            tool_calls = response.choices[0].message.tool_calls
            arguments = tool_calls[0].function.arguments
            arguments = json.loads(arguments)
            fault_segment = arguments.get("fault_segment", None)
            repaired_segment = arguments.get("repaired_segment", None)

            if suggestion and fault_segment and repaired_segment:
                is_repaired = repair_spec_impl(
                    input_spec, fault_segment, repaired_segment, output_spec
                )

        except Exception as e:
            suggestion = str(e)

        patch = get_patch(input_spec, output_spec) if is_repaired else None
        save_log(output_log, is_repaired, log, suggestion, fault_segment, patch)

        return suggestion, is_repaired

    def _prepare_messages(self, spec, log):
        # 准备消息
        messages = []
        if SYSTEM_PROMPT:
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.append(
            {"role": "user", "content": PROMPT_TEMPLATE.format(spec=spec, log=log)}
        )
        return messages

    def _prepare_messages_pro_1(self, spec, log, doc):
        messages = []
        if SYSTEM_PROMPT_PRO:
            messages.append({"role": "system", "content": SYSTEM_PROMPT_PRO})
        messages.append(
            {
                "role": "user",
                "content": PROMPT_TEMPLATE_PRO_1.format(spec=spec, log=log, doc=doc),
            }
        )
        return messages

    def _prepare_messages_pro_2(self, spec, info, doc):
        messages = []
        messages.append(
            {
                "role": "user",
                "content": PROMPT_TEMPLATE_PRO_2.format(spec=spec, info=info, doc=doc),
            }
        )
        return messages

    def _prepare_tools(self):
        # 准备工具
        return [gen_func_description(repair_spec)]

    def _prepare_tools_pro(self):
        # 准备工具
        return [gen_func_description(repair_spec_pro)]

    def _prepare_doc(self, doc_file):
        if doc_file is None:
            return None
        with open(doc_file, "r", encoding="utf-8") as f:
            doc = f.read()
        return doc

    def _preprocess_spec(self, spec_file):
        # 预处理spec
        with open(spec_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        index = 0
        for i in range(len(lines)):
            lines[i] = f"{index}: " + lines[i]
            index += 1
        start_index = 0
        for i in range(len(lines)):
            if "License" in lines[i]:
                start_index = i + 1
                break
            if "BuildRequires" in lines[i]:
                start_index = i
                break
        spec = "".join(lines[start_index:])
        return spec

    def _preprocess_log(self, log_file):
        # 预处理log
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        start_index = 0
        end_index = len(lines)

        for i in range(len(lines) - 1, -1, -1):
            if "Child return code was: 1" in lines[i]:
                end_index = i

            pattern = re.compile(r"^Executing\(%\w+\):")
            if pattern.match(lines[i]):
                start_index = i
                break

        log = "".join(lines[start_index:end_index])

        return log
