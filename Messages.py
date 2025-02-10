import base64
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal


class Memory:
    def __init__(self):
        self.max_size = 100
        self.messages = []

    def get_messages(self):
        return self.messages[-self.max_size :]

    def generate_text_message(self, text: str, role: str):
        return {
            "role": role,
            "content": text,
        }

    def generate_images_message(self, image_urls: List[str], role: str):
        img_messages = {
            "role": role,
            "content": [],
        }

        for image_url in image_urls:
            with open(image_url, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")

            img_messages["content"].append(
                {
                    "type": "imimage_urlage",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                }
            )

        return img_messages

    def generate_tool_call_message(self, tool_call_queries: List[Dict[str, Any]]):
        tool_call_messages = {
            "role": "assistant",
            "tool_calls": [],
        }

        for tool_call_query in tool_call_queries.values():
            tool_call_messages["tool_calls"].append(
                {
                    "id": tool_call_query.id,
                    "type": tool_call_query.type,
                    "function": {
                        "name": tool_call_query.function.name,
                        "arguments": tool_call_query.function.arguments,
                    },
                }
            )
        return tool_call_messages

    def generate_tool_response_message(self, tool_call_response: Dict[str, Any]):
        return {
            "role": "tool",
            "tool_call_id": tool_call_response["tool_call_id"],
            "content": tool_call_response["content"],
        }

    def add_message(
        self,
        text: str = "",
        image_urls: List[str] = [],
        tool_call_queries: List[Dict[str, Any]] = [],
        tool_call_responses: List[Dict[str, Any]] = [],
        role: Literal["developer", "assistant", "user", "tool"] = "user",
    ):
        """添加一条消息
        可以是文字、图片、工具调用
        """

        # 添加文字消息
        if text != "":
            self.messages.append(self.generate_text_message(text, role))

        # 添加图片消息
        if len(image_urls) > 0:
            self.messages.append(self.generate_images_message(image_urls, role))

        # 添加工具调用消息
        if len(tool_call_queries) > 0:
            self.messages.append(self.generate_tool_call_message(tool_call_queries))

        # 添加工具调用结果
        for tool_call_response in tool_call_responses:
            self.messages.append(
                self.generate_tool_response_message(tool_call_response)
            )

    def clear_messages(self):
        self.messages = []
