"""这是一个三角洲今日密码查询插件

提供三角洲行动游戏的今日密码查询功能。
使用 tmini.net API 获取密码数据。
"""

from typing import Dict, List

import httpx
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
    """三角洲今日密码查询配置"""

    API_URL: str = Field(
        default="https://www.tmini.net/api/sjzmm?ckey=&type=",
        title="三角洲今日密码API地址",
        description="三角洲今日密码API的基础URL",
    )
    TIMEOUT: int = Field(
        default=10,
        title="请求超时时间",
        description="API请求的超时时间(秒)",
    )


# 获取配置实例
config: DeltaPasswordConfig = plugin.get_config(DeltaPasswordConfig)


@plugin.mount_sandbox_method(
    SandboxMethodType.AGENT, 
    name="查询三角洲密码", 
    description="查询三角洲行动游戏的今日密码"
)
async def get_delta_password(_ctx: AgentCtx) -> str:
    """查询三角洲行动游戏的今日密码

    Args:
        _ctx: 代理上下文
        
    Returns:
        str: 查询结果字符串，包含所有地点的密码信息。

    Example:
        查询三角洲今日密码:
        get_delta_password()
    """
    try:
        headers = {
            "Content-Type": "application/none"
        }
        
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            response = await client.get(config.API_URL, headers=headers)
            response.raise_for_status()
            text_data = response.text
            
            # 解析文本数据
            lines = text_data.strip().split('\n')
            
            if not lines:
                return "未找到密码信息，请稍后重试。"
            
            # 提取更新日期
            date_line = lines[0]
            if "更新日期:" in date_line:
                date = date_line.replace("更新日期:", "").strip()
            else:
                date = "未知日期"
            
            # 解析地图名称和密码
            password_data = []
            current_map = None
            current_password = None
            
            for line in lines:
                line = line.strip()
                if "地图名称:" in line:
                    current_map = line.replace("地图名称:", "").strip()
                elif "密码:" in line:
                    current_password = line.replace("密码:", "").strip()
                    # 当同时有地图名称和密码时，添加到结果中
                    if current_map and current_password:
                        password_data.append({
                            "location": current_map,
                            "password": current_password
                        })
                        current_map = None
                        current_password = None
            
            if not password_data:
                return f"今日({date})未找到密码信息，请稍后重试。"
            
            # 构建返回结果
            result = [f"三角洲行动今日密码 - {date}"]
            for pwd_info in password_data:
                location = pwd_info.get("location", "未知地点")
                password = pwd_info.get("password", "未知密码")
                result.append(f"  • {location}：{password}")
            
            return "\n".join(result)
            
    except httpx.RequestError as e:
        logger.error(f"请求三角洲今日密码API时出错: {e}")
        return "请求三角洲今日密码API时出错，请稍后重试。"
    except Exception as e:
        logger.exception(f"处理三角洲今日密码API响应时发生未知错误: {e}")
        return "处理三角洲今日密码API响应时出错，请稍后重试。"


@plugin.mount_cleanup_method()
async def clean_up():
    """清理插件资源"""
    logger.info("三角洲今日密码查询插件资源已清理。")