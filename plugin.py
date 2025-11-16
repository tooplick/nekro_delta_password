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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            response = await client.get(config.API_URL, headers=headers)
            response.raise_for_status()
            text_data = response.text
            
            logger.info(f"API返回数据: {text_data[:200]}...")  # 记录前200字符用于调试
            
            # 解析文本数据
            lines = text_data.strip().split('\n')
            
            if not lines:
                return "未找到密码信息，请稍后重试。"
            
            # 提取更新日期
            update_date = "今日"
            for line in lines:
                if "更新日期:" in line:
                    date_part = line.split("更新日期:")[1].strip()
                    if "每日密码" in date_part:
                        update_date = date_part.split("每日密码")[0].strip()
                    else:
                        update_date = date_part
                    break
            
            # 解析地图名称和密码
            password_data = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # 查找地图名称行
                if line.startswith("地图名称:"):
                    location = line.replace("地图名称:", "").strip()
                    
                    # 在接下来的几行中查找密码
                    for j in range(i+1, min(i+10, len(lines))):  # 最多向后查找10行
                        next_line = lines[j].strip()
                        if next_line.startswith("密码:"):
                            password = next_line.replace("密码:", "").strip()
                            password_data.append({
                                "location": location,
                                "password": password
                            })
                            break
            
            if not password_data:
                return f"今日({update_date})未找到密码信息，请稍后重试或检查API格式是否变化。"
            
            # 构建返回结果
            result = [f"三角洲行动{update_date}密码信息："]
            for pwd_info in password_data:
                location = pwd_info.get("location", "未知地点")
                password = pwd_info.get("password", "未知密码")
                result.append(f"  • {location}：{password}")
            
            return "\n".join(result)
            
    except httpx.RequestError as e:
        logger.error(f"请求三角洲今日密码API时出错: {e}")
        return "请求三角洲今日密码API时出错，请检查网络连接后重试。"
    except Exception as e:
        logger.exception(f"处理三角洲今日密码API响应时发生未知错误: {e}")
        return "处理三角洲今日密码API响应时出错，请稍后重试或联系管理员检查插件。"


@plugin.mount_cleanup_method()
async def clean_up():
    """清理插件资源"""
    logger.info("三角洲今日密码查询插件资源已清理。")