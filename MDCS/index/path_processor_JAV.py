# JAV 路径文件名处理器
from collections import namedtuple
from dataclasses import dataclass, field
from enum import Enum
import pathlib
import re

import fuckit
import pydantic
import pydash


class Movie(pydantic.BaseModel):
    """影片信息"""

    class CensoredType(Enum):
        """删减类型"""

        mosaic = 0
        """有"""
        no_mosaic = 1
        """无"""
        cracked = 2
        """破解"""
        leaked = 3
        """流出"""

    censoredType: CensoredType = CensoredType.mosaic
    """删减类型"""
    path: pathlib.Path = None
    """路径"""
    code_of_pre: str = ""
    """预处理后的番号:指根据路径文件名获取的"""
    code_of_net: str = None
    """网络抓取后的准确番号"""
    episode: str = None
    isCnSub: bool = False
    """中文字幕"""


# @dataclass
# class PathMeta:
#     path: str
#     """路径"""
#     code: str = None
#     """番号"""
#     possible_episodes: list[str] = field(default_factory=lambda: [])
#     """可能的集数,过渡用,最终集数使用episode"""
#     episode: str = None
#     """集数"""
#     is_uncensored: bool = False
#     """ 是否无码 """
#     is_cracked: bool = False
#     """ 是否破解 """
#     is_leaked: bool = False
#     """ 是否流出"""
#     is_cn_subs: bool = False
#     """ 是否中字"""


class PathNameProcessor:
    """提取JAV的番号(和动画/欧美分开处理,文件名规律和站点差异都太大)

    Returns:
        _type_: _description_
    """

    # 类变量
    # TODO: 应该读取 ini文件
    pattern_of_file_name_suffixes = r".(mov|mp4|avi|rmvb|wmv|mov|mkv|flv|ts|m2ts|iso)$"

    # def __init__(self):

    @staticmethod
    def remove_distractions(origin_name):
        """移除无意义干扰项"""
        # 移除文件类型后缀
        origin_name = re.sub(
            PathNameProcessor.pattern_of_file_name_suffixes,
            "",
            origin_name,
            0,
            re.IGNORECASE,
        )

        # 处理包含减号-和_的番号'/-070409_621'
        origin_name = re.sub(r"[-_~*# ]", "-", origin_name, 0)

        # 移除无意义字段
        patterns = [
            # TODO: 移除自定义字段的 取自配置文件
            # 移除含有 域名的广告字段
            r"[\w\.\-]+?\.(cc|com|net|me|club|jp|tv|xyz|biz|wiki|info|tw|us|de)@?",
            # 移除字母开头 清晰度相关度 字符(视频质量以分析视频文件获取)
            r"\b(SD|((F|U)|(Full|Ultra)[-_*. ~]?)?HD|BD|(blu[-_*. ~]?ray)|[hx]264|[hx]265|HEVC)\b",
            # 移除数字开头的 清晰度相关度 字符
            r"(?<!\d)(4K|(1080[ip])|(720p)|(480p))",
            # 移除日期字段
            r"(?:-)(19[789]\d|20\d{2})(-?(0\d|1[012])-?(0[1-9]|[12]\d|3[01])?)?[-.]",
            # 其他无意义字段
            r"JAV",
        ]
        # 将多个模式组合成一个大的模式，使用 '|' 作为分隔符
        combined_pattern = "|".join(patterns)
        # 批量处理
        origin_name = re.sub(combined_pattern, "-",
                             origin_name, flags=re.IGNORECASE)
        # 移除连续重复无意义符号-
        origin_name = re.sub(r"([-.])(\1+)", r"\1", origin_name)
        # 移除尾部无意义符号 方便识别剧集数
        origin_name = re.sub(r"[-.]+$", "", origin_name)

        return origin_name

    @staticmethod
    def extract_suffix_episode(origin_name):
        """提取尾部集数号 1-9,a-z(只识别1-2位) part1 ，ipz.A  ， CD1 ， NOP019B.HD.wmv"""
        episode = None
        name = origin_name
        with fuckit:
            # 零宽断言获取尾部数字 剧集数 123
            pattern_episodes_number = r"(?<!\d)\d{1,2}$"
            episode = re.findall(pattern_episodes_number, origin_name)[-1]
            name = re.sub(pattern_episodes_number, "", origin_name)

        with fuckit:
            # 零宽断言获取尾部字幕 剧集数 abc
            pattern_episodes_alpha = r"(?<![a-zA-Z])[a-zA-Z]$"
            episode = re.findall(pattern_episodes_alpha,
                                 origin_name)[-1].upper()
            name = re.sub(pattern_episodes_alpha, "", origin_name)

        return episode, name

    @staticmethod
    def extract_code(origin_name):
        """
        提取集数 和 规范过的番号
        """
        episode = None
        code = None

        chinese_subtitles_match = re.search(
            r"(?<![a-zA-Z])(ch\b)|(中?文?字幕?)", origin_name, re.IGNORECASE
        )  # 这里不匹配C 是可能是 集数ABC, 后面再判断C是不是 中字
        uncensored_match = re.search(
            r"(unc?e?n?s?o?r?e?d?)|(无码)", origin_name, re.IGNORECASE
        )
        # TODO: 取ini uncensored_prefix ,如果匹配,也为 uncensored
        leak_match = re.search(r"(leak(ed)?)|(泄漏)|(流出)",
                               origin_name, re.IGNORECASE)
        crack_match = re.search(r"(crack(ed)?)|(破解)",
                                origin_name, re.IGNORECASE)
        # 使用 reduce 来 移除 匹配到的 字段, 以减少后面 番号识别的干扰
        matches = [
            match
            for match in [
                chinese_subtitles_match,
                uncensored_match,
                leak_match,
                crack_match,
            ]
            if match
        ]
        origin_name = pydash.reduce_(
            matches, lambda a, i: a[: i.start()] + a[i.end():], origin_name
        )

        # TODO: code匹配 1. 优先匹配ini配置的正则规则(未施工)

        # 2:匹配比较特殊的规则, 按javdb数据源的命名规范提取number
        common_code_matches = {
            "tokyo.*hot": lambda x: str(
                re.search(r"(cz|gedo|k|n|red-|se)\d{2,4}", x, re.I).group()
            ),
            "carib": lambda x: str(
                re.search(r"\d{6}(-|_)\d{3}", x, re.I).group()
            ).replace("-", "_"),
            "1pon|mura|paco": lambda x: str(
                re.search(r"\d{6}(-|_)\d{3}", x, re.I).group()
            ).replace("-", "_"),
            "10mu": lambda x: str(
                re.search(r"\d{6}(-|_)\d{2}", x, re.I).group()
            ).replace("-", "_"),
            "x-art": lambda x: str(
                re.search(r"x-art\.\d{2}\.\d{2}\.\d{2}", x, re.I).group()
            ),
            "xxx-av": lambda x: "".join(
                ["xxx-av-",
                    re.findall(r"xxx-av[^\d]*(\d{3,5})[^\d]*", x, re.I)[0]]
            ),
            "heydouga": lambda x: "heydouga-"
            + "-".join(re.findall(r"(\d{4})[\-_](\d{3,4})[^\d]*", x, re.I)[0]),
            "heyzo": lambda x: "HEYZO-" + re.findall(r"heyzo[^\d]*(\d{4})", x, re.I)[0],
            "mdbk": lambda x: str(re.search(r"mdbk(-|_)(\d{4})", x, re.I).group()),
            "mdtm": lambda x: str(re.search(r"mdtm(-|_)(\d{4})", x, re.I).group()),
            "caribpr": lambda x: str(
                re.search(r"\d{6}(-|_)\d{3}", x, re.I).group()
            ).replace("-", "_"),
        }
        if (
            partern := pydash.find(
                common_code_matches, lambda v, k: re.search(
                    k, origin_name, re.I)
            )
        ) is not None and (code := partern(origin_name)) is not None:
            episode = PathNameProcessor.extract_episode_behind_code(
                origin_name, code)
        else:
            # 3 通用规则: 找到含- 或不含-的 番号：1. 数字+数字 2. 字母+数字
            code = re.findall(
                r"(?:\d{2,}-\d{2,})|(?:[A-Z]+-?[A-Z]*\d{2,})", origin_name
            )[-1]
            episode = PathNameProcessor.extract_episode_behind_code(
                origin_name, code)
            # 将无-的名字处理加上-
            if not ("-" in code):
                # 无减号-的番号,尝试分段加上-
                # 非贪婪匹配非特殊字符，零宽断言后，数字至少2位连续,ipz221.part2 ， mide072hhb ,n1180
                with fuckit:
                    code = re.findall(r"[a-zA-Z]+\d{2,}", code)[-1]
                    # 比如MCDV-47 mcdv-047 是2个不一样的片子，但是 SIVR-00008 和 SIVR-008是同同一部,但是heyzo除外,heyzo 是四位数
                    if "heyzo" not in code.lower():
                        code = re.sub(
                            r"([a-zA-Z]{2,})(?:0*?)(\d{2,})", r"\1-\2", code)

            # 正则取含-的番号 【字母-[字母]数字】,数字必定大于2位 番号的数组的最后的一个元素
            with fuckit:
                # MKBD_S03-MaRieS
                code = re.findall(r"[a-zA-Z|\d]+-[a-zA-Z|\d]*\d{2,}", code)[-1]
                # 107NTTR-037 -> NTTR-037 , SIVR-00008 -> SIVR-008 ，但是heyzo除外
                if "heyzo" not in code.lower():
                    searched = re.search(
                        r"([a-zA-Z]{2,})-(?:0*)(\d{3,})", code)
                    if searched:
                        code = "-".join(searched.groups())

        return namedtuple(
            "Code",
            [
                "code",
                "episode",
                "is_uncensored",
                "is_cracked",
                "is_leaked",
                "is_cn_subs",
            ],
        )(
            code,
            episode,
            bool(uncensored_match),
            bool(crack_match),
            bool(leak_match),
            bool(chinese_subtitles_match),
        )

    @staticmethod
    def extract_episode_behind_code(origin_name, code):
        episode = None

        with fuckit:
            # 零宽断言获取尾部字幕 剧集数 abc123
            result_dict = re.search(
                rf"(?<={code})-?((?P<alpha>(\b[A-Z]\b))|\w*(?P<num>\d(?!\d)))",
                origin_name,
                re.I,
            ).groupdict()
            episode = result_dict["num"] or result_dict["alpha"]
        return episode.upper() if episode else None


def safe_list_get(list_in, idx, default):
    try:
        return list_in[idx]
    except IndexError:
        return default
