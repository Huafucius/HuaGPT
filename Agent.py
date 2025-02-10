import rich.console
from openai import OpenAI
from Messages import Memory
from AgentTool import AgentTool


class Agent:
    def __init__(self):
        self.console = rich.console.Console()
        self.model = OpenAI()
        self.memory = Memory()
        self.tools = AgentTool()

    def use_model(self, model_name: str = "gpt-4o-mini"):
        response = self.model.chat.completions.create(
            messages=self.memory.get_messages(),
            model=model_name,
            stream=True,
            tools=self.tools.get_tools(),
        )

        # AI回复
        response_text, tool_call_query = self.print_ai_message(response)

        # AI文本
        if response_text != "":
            self.memory.add_message(text=response_text, role="assistant")

        return response_text, tool_call_query

    def chat(self, query: str, images_urls: list[str] = [], model: str = "gpt-4o-mini"):
        """调用AI进行一轮对话"""

        # 用户输入
        self.memory.add_message(text=query, image_urls=images_urls, role="user")

        # 调用AI接口
        response_text, tool_call_query = self.use_model(model)

        # AI工具调用
        if tool_call_query != {}:
            self.memory.add_message(tool_call_queries=tool_call_query, role="assistant")
            tool_call_responses = self.print_tool_messages(tool_call_query)
            self.memory.add_message(
                tool_call_responses=tool_call_responses, role="tool"
            )

            # 再次调用AI接口获取回答
            response_text = self.use_model(model)

        return response_text

    def print_user_message(self, query: str):
        """打印传入的用户消息"""
        self.console.print("User:", style="bold blue")
        self.console.print(query, style="blue")

    def print_ai_message(self, response):
        """流式打印AI回复
        返回AI回复的文本和tool_calls"""
        self.console.print("AI:", style="bold green")
        response_text = ""
        tool_call_query = {}
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                self.console.print(
                    chunk.choices[0].delta.content, style="green", end=""
                )
                response_text += chunk.choices[0].delta.content

            for tool_call in chunk.choices[0].delta.tool_calls or []:
                index = tool_call.index

                if index not in tool_call_query:
                    tool_call_query[index] = tool_call

                tool_call_query[
                    index
                ].function.arguments += tool_call.function.arguments

        return response_text, tool_call_query

    def print_tool_messages(self, tool_calls: list):
        """打印工具调用的结果"""
        if tool_calls is not None:
            self.console.print("AIToolCallAsk:", style="bold red")
            self.console.print(tool_calls, style="red")

            self.console.print("AIToolCallAnswer:", style="bold red")
            tool_call_results = self.tools.use_tools(tool_calls)

            for tool_call_result in tool_call_results:
                self.console.print(tool_call_result, style="red")

        return tool_call_results

    def add_tools(self, func_list: list):
        """给出一个函数列表"""
        self.tools.add_tools(func_list)
