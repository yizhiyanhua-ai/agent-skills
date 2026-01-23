"""
MV Skill 异常定义
"""


class MVSkillError(Exception):
    """MV Skill 基础异常类"""
    pass


class MusicGenerationError(MVSkillError):
    """音乐生成失败"""
    pass


class AssetNotFoundError(MVSkillError):
    """素材获取失败"""
    pass


class AssetQualityError(MVSkillError):
    """素材质量不符合要求"""
    pass


class RenderError(MVSkillError):
    """渲染失败"""
    pass


class APIQuotaExceeded(MVSkillError):
    """API 配额用尽"""
    pass


class TemplateNotFoundError(MVSkillError):
    """模板不存在"""
    pass


class StoryboardValidationError(MVSkillError):
    """分镜脚本验证失败"""
    pass


class SessionError(MVSkillError):
    """会话管理错误"""
    pass


class DependencyError(MVSkillError):
    """依赖检查失败"""
    pass
