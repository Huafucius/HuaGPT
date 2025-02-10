from Agent import Agent


def add_two_numbers(a: int, b: int):
    """
    两数相加

    Args:
        a: 第一个数
        b: 第二个数

    Returns:
        相加结果
    """
    return f"{a} + {b} = {a + b}"


def get_weather(city: str):
    """
    获取城市的天气

    Args:
        city: 城市名

    Returns:
        天气情况
    """
    return f"{city}的天气是晴朗的"


agent = Agent()
agent.add_tools([add_two_numbers, get_weather])
agent.chat("今天北京天气如何")
agent.chat("2+2=?")
print(agent.memory.messages)
