import json
from typing import List, Optional

from sqlmodel import Relationship, SQLModel, Field, create_engine, Column, JSON, Session, select
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
    code: str | None = None
    """番号"""
    possible_episodes: List[str] = Field(default=[], sa_column=Column(JSON))
    """可能的集数,过渡用,最终集数使用episode"""
    episode: Optional[str] = None
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
    with Session(engine) as session:
        index = Index()
        session.add(index)
        session.flush()  # 刷新会话，获取 index 的 ID

        # 批量查询已存在的路径
        existing_paths = {p.path for p in session.exec(select(PathMeta)).all()}

        new_path_metas = []
        for path_meta in pathList:
            if path_meta.path in existing_paths:
                LOGGER.warning(f"跳过插入已存在的文件 {path_meta.path} ")
            else:
                path_meta.index_id = index.id
                new_path_metas.append(path_meta)
                existing_paths.add(path_meta.path)  # 更新已存在的路径集合

        # 批量插入新的路径
        if new_path_metas:
            session.add_all(new_path_metas)
            session.commit()  # 提交会话
            LOGGER.info(f"索引完毕:索引路径信息已写入数据库")
        else:
            LOGGER.info("索引完毕:没有新路径被添加")
