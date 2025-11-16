"""
三角洲每日密码查询插件
从 tmini.net API 获取每日地图密码
"""

from typing import Dict
import httpx
import re
from nekro_agent.api.schemas import AgentCtx
from nekro_agent.core import logger
from nekro_agent.services.plugin.base import ConfigBase, NekroPlugin, SandboxMethodType
from pydantic import Field

# 插件元信息
plugin = NekroPlugin(
    name="三角洲今日密码查询插件",
    module_name="delta_password",
    description="提供三角洲行动游戏的今日密码查询功能",
    version="1.0.0",
    author="GeQian",
    url="https://github.com/tooplick/nekro_delta_password",
)

# 插件配置
@plugin.mount_config()
class DeltaPasswordConfig(ConfigBase):
    """三角洲密码 API 配置"""

    API_URL: str = Field(
        default="https://www.tmini.net/api/sjzmm?ckey=&type=",
        title="三角洲API地址",
        description="每日密码查询API"
    )
    TIMEOUT: int = Field(
        default=10,
        title="请求超时时间",
        description="API请求超时时间（秒）"
    )

# 获取配置
config: DeltaPasswordConfig = plugin.get_config(DeltaPasswordConfig)

# 插件方法
@plugin.mount_sandbox_method(
    SandboxMethodType.AGENT,
    name="查询三角洲每日密码",
    description="从 tmini.net 查询今日所有地图的密码，并显示更新日期"
)
async def get_delta_password(_ctx: AgentCtx) -> str:
    """
    查询三角洲每日地图密码，并显示更新日期。
    
    Returns:
        str: 格式化后的密码信息，包括更新日期
    """
    try:
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            response = await client.get(config.API_URL)
            response.raise_for_status()
            response_text = response.text

        # 提取更新日期
        date_match = re.search(r'更新日期[:：]\s*([^\n]+)', response_text)
        update_date = date_match.group(1).strip() if date_match else "未知日期"

        # 正则提取地图名称和密码
        pattern = r"地图名称:\s*([^\n]+)\s*密码:\s*(\d+)"
        matches = re.findall(pattern, response_text)

        if not matches:
            logger.warning("密码API返回格式异常或无数据")
            return f"{update_date}：未能获取到今日三角洲地图密码，请稍后再试。"

        # 转换为字典
        result: Dict[str, str] = {map_name.strip(): password.strip() for map_name, password in matches}

        # 格式化输出
        output_lines = [f"密码更新日期: {update_date}", ""]
        for map_name, pwd in result.items():
            output_lines.append(f"  {map_name}: {pwd}")

        logger.info("成功获取三角洲每日密码")
        return "\n".join(output_lines)

    except Exception as e:
        logger.exception(f"查询三角洲每日密码出错: {e}")
        return "查询三角洲每日密码时发生错误，请稍后重试。"
