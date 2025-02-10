import json
import inspect
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Literal, Union


class ToolDesc(BaseModel):
    type: str = "function"
    function: Dict[str, Any]


class AgentTool:
    def __init__(self):
        self.tool_list = {}
        self.tool_desc_list = []

    def get_tools(self):
        return self.tool_desc_list

    def add_tools(self, func_list: list):
        """把函数列表转换成tool列表"""
        for func in func_list:
            tool_desc = ToolDesc(
                function=self.create_json_schema_from_function(func),
            )

            self.tool_list[func.__name__] = func
            self.tool_desc_list.append(tool_desc.model_dump())
        return

    def use_tools(self, tool_messages):
        """根据AI返回的tool_calls调用对应的函数
        返回一个tool的消息列表
        """
        tool_call_responses = []
        for _, tool_message in tool_messages.items():
            # 获取函数名和参数
            func_name = tool_message.function.name
            function = self.tool_list[func_name]
            func_args = json.loads(tool_message.function.arguments)

            # 调用函数
            content = function(**func_args)
            tool_call_responses.append(
                {
                    "tool_call_id": tool_message.id,
                    "content": str(content),
                }
            )

        return tool_call_responses

    def clear_tools(self):
        self.tool_list = []
        self.func_list = {}
        return

    @staticmethod
    def create_json_schema_from_function(func):
        """给出一个函数
        返回一个符合openai的json schema的字典
        """

        model_json_schema = {}
        model_json_schema["name"] = func.__name__
        model_json_schema["description"] = func.__doc__
        model_json_schema["strict"] = True
        model_json_schema["parameters"] = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        type_map = {
            str: "string",
            int: "number",
            float: "number",
        }

        # 从函数签名中提取参数信息
        # 分别提取模型的参数名、类型、枚举值
        sig = inspect.signature(func)
        properties = {}
        required = []
        for param in sig.parameters.values():
            # 获取参数名
            param_name = str(param.name)

            # 从注解中获取参数类型, 默认为string
            if param.annotation not in type_map:
                param_type = "string"
            else:
                param_type = type_map[param.annotation]

            # 如果是Literal则获取参数枚举值
            if param.annotation is Literal:
                param_type = "string"
                param_enum = [value for value in param.annotation.__args__]
            else:
                param_enum = None

            # 将字段信息添加到字典中
            properties[param_name] = {"type": param_type}
            if param_enum is not None:
                properties[param_name]["enum"] = param_enum

            # 严格模式所有参数都是必须的
            required.append(param_name)

        # 将参数信息添加到json schema中
        model_json_schema["parameters"]["properties"] = properties
        model_json_schema["parameters"]["required"] = required

        return model_json_schema
