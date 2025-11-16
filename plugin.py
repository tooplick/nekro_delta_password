"""这是一个三角洲今日密码查询插件

提供三角洲行动游戏的今日密码查询功能。
使用 tmini.net API 获取密码数据。
"""

from typing import Dict, List
import re

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
    version="1.1.0",
    author="GeQian",
    url="https://github.com/tooplick/nekro_delta_password",
)


# 插件配置
@plugin.mount_config()
class DeltaPasswordConfig(ConfigBase):
    """三角洲今日密码查询配置

    配置插件使用的API地址和请求超时时间。
    """

    API_URL: str = Field(
        default="https://www.tmini.net/api/sjzmm?ckey=&type=",
        title="API地址",
        description="三角洲今日密码API的基础URL地址",
    )
    
    TIMEOUT: int = Field(
        default=15,
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
        logger.info("开始获取三角洲今日密码...")
        
        # 使用更合适的请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        async with httpx.AsyncClient(timeout=config.TIMEOUT) as client:
            response = await client.get(config.API_URL, headers=headers)
            response.raise_for_status()
            text_data = response.text
            
            logger.info(f"API响应成功，数据长度: {len(text_data)}")
            
            # 使用正则表达式提取地图和密码
            password_data = []
            
            # 正则表达式匹配模式：地图名称: 值 和 密码: 值
            pattern = r'地图名称:\s*([^\n]+?)\s*密码:\s*([^\n]+)'
            matches = re.findall(pattern, text_data)
            
            for location, password in matches:
                location = location.strip()
                password = password.strip()
                password_data.append({
                    "location": location,
                    "password": password
                })
                logger.info(f"解析到密码: {location} - {password}")
            
            # 如果正则表达式没找到，尝试备用方法
            if not password_data:
                logger.info("正则表达式未找到数据，尝试备用解析方法")
                password_data = parse_fallback(text_data)
            
            if not password_data:
                return "今日未找到密码信息，请稍后重试。"
            
            # 提取更新日期
            update_date = extract_update_date(text_data)
            
            # 构建返回结果
            result = [f"三角洲行动{update_date}密码信息："]
            for pwd_info in password_data:
                location = pwd_info.get("location", "未知地点")
                password = pwd_info.get("password", "未知密码")
                result.append(f"  • {location}：{password}")
            
            return "\n".join(result)
            
    except httpx.TimeoutException:
        logger.error("请求三角洲今日密码API超时")
        return "请求超时，请稍后重试。"
    except httpx.RequestError as e:
        logger.error(f"请求三角洲今日密码API时出错: {e}")
        return "请求三角洲今日密码API时出错，请检查网络连接后重试。"
    except httpx.HTTPStatusError as e:
        logger.error(f"API返回错误状态码: {e.response.status_code}")
        return f"API服务器返回错误，状态码: {e.response.status_code}"
    except Exception as e:
        logger.exception(f"处理三角洲今日密码API响应时发生错误: {e}")
        return f"处理数据时发生错误: {str(e)}"


def parse_fallback(text_data: str) -> List[Dict]:
    """备用解析方法"""
    password_data = []
    lines = text_data.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith("地图名称:"):
            location = line.replace("地图名称:", "").strip()
            
            # 向后查找密码
            j = i + 1
            while j < len(lines) and j < i + 5:
                next_line = lines[j].strip()
                if next_line.startswith("密码:"):
                    password = next_line.replace("密码:", "").strip()
                    password_data.append({
                        "location": location,
                        "password": password
                    })
                    i = j  # 跳过已处理的行
                    break
                j += 1
        i += 1
    
    return password_data


def extract_update_date(text_data: str) -> str:
    """提取更新日期"""
    lines = text_data.strip().split('\n')
    for line in lines:
        if "更新日期:" in line:
            date_part = line.split("更新日期:")[1].strip()
            if "每日密码" in date_part:
                return date_part.split("每日密码")[0].strip()
            return date_part
    return "今日"


@plugin.mount_cleanup_method()
async def clean_up():
    """清理插件资源"""
    logger.info("三角洲今日密码查询插件资源已清理。")