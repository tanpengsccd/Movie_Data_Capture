import re

import fuckit


class PathNameProcessor:
    """提取 Japan AV的番号(建议和动画/欧美分开处理,文件名规律和站点差异都太大)

    Returns:
        _type_: _description_
    """
    # 类变量
    pattern_of_file_name_suffixes = r'.(mov|mp4|avi|rmvb|wmv|mov|mkv|flv|ts|m2ts)$'

    # def __init__(self):

    @staticmethod
    def remove_distractions(origin_name):
        """移除干扰项"""
        # 移除文件类型后缀
        origin_name = re.sub(PathNameProcessor.pattern_of_file_name_suffixes, '', origin_name, 0, re.IGNORECASE)

        # 处理包含减号-和_的番号'/-070409_621'
        origin_name = re.sub(r'[-_~*# ]', "-", origin_name, 0)
        
        patterns = [
            r'JAV',
            r'22-sht.me',
        ]
        # 将多个模式组合成一个大的模式，使用 '|' 作为分隔符
        combined_pattern = '|'.join(patterns)
        # 批量处理 
        origin_name = re.sub(combined_pattern, '-', origin_name, flags=re.IGNORECASE)

        
        # origin_name = re.sub(r'(Carib)(bean|ean)?', '-', origin_name, 0, re.IGNORECASE)
        # origin_name = re.sub(r'(1pondo)', '-', origin_name, 0, re.IGNORECASE)
        # origin_name = re.sub(r'(tokyo)[-. ]?(hot)', '-', origin_name, 0, re.IGNORECASE)
        # origin_name = re.sub(r'Uncensored', '-', origin_name, 0, re.IGNORECASE)
        # origin_name = re.sub(r'JAV', '-', origin_name, 0, re.IGNORECASE)
        # 移除干扰字段
        # origin_name = origin_name.replace('22-sht.me', '-')

        # 去除文件名中时间 1970-2099年 月 日
        pattern_of_date = r'(?:-)(19[789]\d|20\d{2})(-?(0\d|1[012])-?(0[1-9]|[12]\d|3[01])?)?[-.]'
        # 移除字母开头 清晰度相关度 字符
        pattern_of_resolution_alphas = r'\b(SD|((F|U)|(Full|Ultra)[-_*. ~]?)?HD|BD|(blu[-_*. ~]?ray)|[hx]264|[hx]265|HEVC)\b'
        # 数字开头的 清晰度相关度 字符
        pattern_of_resolution_numbers = r'(?<!\d)(4K|(1080[ip])|(720p)|(480p))'
        origin_name = re.sub(pattern_of_resolution_alphas, "-", origin_name, 0, re.IGNORECASE)
        origin_name = re.sub(pattern_of_resolution_numbers, "-", origin_name, 0, re.IGNORECASE)
        origin_name = re.sub(pattern_of_date, "-", origin_name)

        if 'FC2' or 'fc2' in origin_name:
            origin_name = origin_name.replace('-PPV', '').replace('PPV-', '').replace('FC2PPV-', 'FC2-').replace(
                'FC2PPV_', 'FC2-')

        # 移除连续重复无意义符号-
        origin_name = re.sub(r"([-.])(\1+)", r"\1", origin_name)
        # 移除尾部无意义符号 方便识别剧集数
        origin_name = re.sub(r'[-.]+$', "", origin_name)

        return origin_name

    @staticmethod
    def extract_suffix_episode(origin_name):
        """ 提取尾部集数号 1-9,a-z(只识别一位) part1 ，ipz.A  ， CD1 ， NOP019B.HD.wmv"""
        episode = None
        with fuckit:
            # 零宽断言获取尾部数字 剧集数 123
            pattern_episodes_number = r'(?<!\d)\d$'
            episode = re.findall(pattern_episodes_number, origin_name)[-1]
            origin_name = re.sub(pattern_episodes_number, "", origin_name)
        with fuckit:
            # 零宽断言获取尾部字幕 剧集数 abc
            pattern_episodes_alpha = r'(?<![a-zA-Z])[a-zA-Z]$'
            episode = re.findall(pattern_episodes_alpha, origin_name)[-1]
            origin_name = re.sub(pattern_episodes_alpha, "", origin_name)
        return episode, origin_name

    @staticmethod
    def extract_code(origin_name):
        """
        提取集数和 规范过的番号
        """
        name = None
        episode = None
        with fuckit:
            # 优先匹配 固定正则 
            patterns = [
                r'JAV',
                r'22-sht.me',
            ]
            
            # origin_name = re.sub(r'(Carib)(bean|ean)?', '-', origin_name, 0, re.IGNORECASE)
            # origin_name = re.sub(r'(1pondo)', '-', origin_name, 0, re.IGNORECASE)
            # origin_name = re.sub(r'(tokyo)[-. ]?(hot)', '-', origin_name, 0, re.IGNORECASE)
            # origin_name = re.sub(r'Uncensored', '-', origin_name, 0, re.IGNORECASE)
            # origin_name = re.sub(r'JAV', '-', origin_name, 0, re.IGNORECASE)
            
            # 找到含- 或不含-的 番号：1. 数字+数字 2. 字母+数字
            name = re.findall(r'(?:\d{2,}-\d{2,})|(?:[A-Z]+-?[A-Z]*\d{2,})', origin_name)[-1]
            episode = PathNameProcessor.extract_episode_behind_code(origin_name, name)
            # 将未-的名字处理加上 -
            if not ('-' in name):
                # 无减号-的番号,尝试分段加上-
                # 非贪婪匹配非特殊字符，零宽断言后，数字至少2位连续,ipz221.part2 ， mide072hhb ,n1180
                with fuckit:
                    name = re.findall(r'[a-zA-Z]+\d{2,}', name)[-1]
                    # 比如MCDV-47 mcdv-047 是2个不一样的片子，但是 SIVR-00008 和 SIVR-008是同同一部,但是heyzo除外,heyzo 是四位数
                    if "heyzo" not in name.lower():
                        name = re.sub(r'([a-zA-Z]{2,})(?:0*?)(\d{2,})', r'\1-\2', name)

            # 正则取含-的番号 【字母-[字母]数字】,数字必定大于2位 番号的数组的最后的一个元素
            with fuckit:
                # MKBD_S03-MaRieS
                name = re.findall(r'[a-zA-Z|\d]+-[a-zA-Z|\d]*\d{2,}', name)[-1]
                # 107NTTR-037 -> NTTR-037 , SIVR-00008 -> SIVR-008 ，但是heyzo除外
                if "heyzo" not in name.lower():
                    searched = re.search(r'([a-zA-Z]{2,})-(?:0*)(\d{3,})', name)
                    if searched:
                        name = '-'.join(searched.groups())

        return episode, name

    @staticmethod
    def extract_episode_behind_code(origin_name, code):
        episode = None

        with fuckit:
            # 零宽断言获取尾部字幕 剧集数 abc123
            result_dict = re.search(rf'(?<={code})-?((?P<alpha>([A-Z](?![A-Z])))|(?P<num>\d(?!\d)))', origin_name,
                                    re.I).groupdict()
            episode = result_dict['alpha'] or result_dict['num']
        return episode


def safe_list_get(list_in, idx, default):
    try:
        return list_in[idx]
    except IndexError:
        return default
