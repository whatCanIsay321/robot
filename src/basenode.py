import json
from typing import Any, Dict
from langgraph.types import Command
from loguru import logger


class BaseNode:
    """
    LangGraph 基类节点，统一封装：
    - 异常处理
    - IoC 依赖注入
    - 输出格式规范化
    - 调用日志
    """

    name: str = "base_node"
    next_step: str | None = None

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """子类需重写此方法，实现具体逻辑"""
        raise NotImplementedError("Subclasses must implement `run` method")

    async def __call__(self, state: Dict[str, Any]) -> Command:
        """LangGraph 标准入口"""
        try:
            logger.info(f"➡️ Executing node: {self.name}")
            update = await self.run(state)
            goto = update.pop("goto", self.next_step)
            logger.info(f"✅ Node {self.name} completed, next: {goto}")
            return Command(update=update, goto=goto)
        except Exception as e:
            logger.exception(f"❌ Error in node {self.name}: {e}")
            return Command(update={"error": str(e)}, goto="agent_finish")
