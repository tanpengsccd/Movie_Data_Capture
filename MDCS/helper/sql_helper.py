import json
from typing import List

from sqlmodel import Relationship, SQLModel, Field, create_engine, Column, JSON
from datetime import datetime, timedelta, timezone
from helper.loguru_config import logu


LOGGER = logu(__name__)


class Index(SQLModel, table=True):
    """创建索引的记录表,索引一次 生成一次"""
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=8))))
    """ 创建时间 """
    path_metas: List["PathMeta"] = Relationship(back_populates="index")


class PathMeta(SQLModel, table=True):
    """索引的视频路径 持久化的原因: 为了追溯历史视频名字,可用于 1.还原视频路径 2.出错时可分析原视频路径"""
    id: int = Field(default=None, primary_key=True)
    # 关联 Index的id
    index_id: int = Field(foreign_key="index.id")
    index: Index = Relationship(back_populates="path_metas")

    path: str = Field(unique=True)
    """路径"""
    code: str = None
    """番号"""
    possible_episodes: List[str] = Field(default=[], sa_column=Column(JSON))
    """可能的集数,过渡用,最终集数使用episode"""
    episode: str = None
    """集数"""
    is_uncensored: bool = False
    """ 是否无码 """
    is_cracked: bool = False
    """ 是否破解 """
    is_leaked: bool = False
    """ 是否流出(这个字段不好获取,一般流出都归类到无码了)"""
    is_cn_subs: bool = False
    """ 是否中字"""
    # timezone shanghai
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=8))))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(hours=8))))
    is_deleted: bool = False
    """ 是否已经删除 """


engine = create_engine("sqlite:///mdcs.db")
SQLModel.metadata.create_all(engine)


def insert_path_meta_list(pathList: List[PathMeta]):
    with SQLModel.Session(engine) as session:
        index = Index()
        session.add(index)
        session.flush()  # 刷新会话，获取 index 的 ID
        map(lambda path_meta: setattr(path_meta, 'index_id', index.id), pathList)  # 设置 index_id
        # 批量添加 PathMeta 对象
        session.add_all(pathList)
        session.commit()  # 提交会话

    LOGGER.info(f"索引路径信息已写入数据库")
