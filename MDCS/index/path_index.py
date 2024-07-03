from collections import namedtuple
import copy
from itertools import groupby
import os
from pathlib import Path
import re
from typing import List

import pydash
from helper.global_config import config
from .path_processor_JAV import PathMeta, PathNameProcessor
# 获取待处理文件列表: 会按配置规则过滤不相关文件,新增失败文件列表跳过处理，及.nfo修改天数跳过处理，提示跳过视频总数，调试模式(-g)下详细被跳过文件，跳过小广告


def movie_lists(source_folder, regexstr: str) -> List[str]:
    # debug = G_conf.debug()
    # nfo_skip_days = G_conf.nfo_skip_days()
    # link_mode = G_conf.link_mode()
    file_type = config.index.file_name_suffixes
    # trailerRE = re.compile(r'-trailer\.', re.IGNORECASE)
    # cliRE = re.compile(regexstr, re.IGNORECASE) if isinstance(
    #     regexstr, str) and len(regexstr) else None
    # failed_list_txt_path = Path(
    #     G_conf.failed_folder()).resolve() / 'failed_list.txt'
    # # 提取历史刮削失败的路径
    # failed_set = set()
    # if (G_conf.main_mode() == Main_Mode.ScrapingInAnalysisFolder or link_mode) and not G_conf.ignore_failed_list():
    #     try:
    #         flist = failed_list_txt_path.read_text(
    #             encoding='utf-8').splitlines()
    #         failed_set = set(flist)
    #         if len(flist) != len(failed_set):  # 检查去重并写回，但是不改变failed_list.txt内条目的先后次序，重复的只保留最后的
    #             fset = failed_set.copy()
    #             for i in range(len(flist) - 1, -1, -1):
    #                 fset.remove(flist[i]) if flist[i] in fset else flist.pop(i)
    #             failed_list_txt_path.write_text(
    #                 '\n'.join(flist) + '\n', encoding='utf-8')
    #             assert len(fset) == 0 and len(flist) == len(failed_set)
    #     except:
    #         pass

    if not Path(source_folder).is_dir():
        raise FileNotFoundError(source_folder)

    total = []
    source = Path(source_folder).resolve()
    skip_failed_cnt, skip_nfo_days_cnt = 0, 0
    # escape_folder_set = set(re.split("[,，]", G_conf.escape_folder()))
    # 遍历文件夹
    for full_name in source.glob(r'**/*'):
        # 原路径刮削
        # if G_conf.main_mode() != Main_Mode.ScrapingInAnalysisFolder and set(full_name.parent.parts) & escape_folder_set:
        #     continue
        # 不是文件
        if not full_name.is_file():
            continue
        # 不是指定类型
        if not full_name.suffix.lower() in file_type:
            continue
        absf = str(full_name)

        is_sym = full_name.is_symlink()
        is_hard_link = full_name.stat().st_nlink > 1
        # if G_conf.main_mode() != Main_Mode.ScrapingInAnalysisFolder and (is_sym or (
        #         full_name.stat().st_nlink > 1 and not G_conf.scan_hardlink())):  # 短路布尔 符号链接不取stat()，因为符号链接可能指向不存在目标
        #     continue  # 模式不等于3下跳过软连接和未配置硬链接刮削
        # 调试用0字节样本允许通过，去除小于120MB的广告'苍老师强力推荐.mp4'(102.2MB)'黑道总裁.mp4'(98.4MB)'有趣的妹子激情表演.MP4'(95MB)'有趣的臺灣妹妹直播.mp4'(15.1MB)
        # 同上 符号链接不取stat()及st_size，直接赋0跳过小视频检测
        movie_size = 0 if is_sym else full_name.stat().st_size
        # if 0 < movie_size < 125829120:  # 1024*1024*120=125829120
        #     continue
        # if cliRE and not cliRE.search(absf) or trailerRE.search(full_name.name):
        # continue
        # if G_conf.main_mode() == Main_Mode.ScrapingInAnalysisFolder:
        #     nfo = full_name.with_suffix('.nfo')
        #     if not nfo.is_file():
        #         if debug:
        #             print(f"[!]Metadata {nfo.name} not found for '{absf}'")
        #     elif nfo_skip_days > 0 and file_modification_days(nfo) <= nfo_skip_days:
        #         skip_nfo_days_cnt += 1
        #         if debug:
        #             print(
        #                 f"[!]Skip movie by it's .nfo which modified within {nfo_skip_days} days: '{absf}'")
        #         continue
        total.append(absf)

    # if skip_failed_cnt:
    #     print(
    #         f"[!]Skip {skip_failed_cnt} movies in failed list '{failed_list_txt_path}'.")
    # if skip_nfo_days_cnt:
    #     print(
    #         f"[!]Skip {skip_nfo_days_cnt} movies in source folder '{source}' who's .nfo modified within {nfo_skip_days} days.")
    # if nfo_skip_days <= 0 or not link_mode or G_conf.main_mode() == Main_Mode.ScrapingInAnalysisFolder:
    #     return total
    # 软连接方式，已经成功削刮的也需要从成功目录中检查.nfo更新天数，跳过N天内更新过的
    # skip_numbers = set()
    # success_folder = Path(G_conf.success_folder()).resolve()
    # for f in success_folder.glob(r'**/*'):
    #     if not re.match(r'\.nfo$', f.suffix, re.IGNORECASE):
    #         continue
    #     if file_modification_days(f) > nfo_skip_days:
    #         continue
    #     number = get_number(False, f.stem)
    #     if not number:
    #         continue
    #     skip_numbers.add(number.lower())

    # rm_list = []
    # for f in total:
    #     n_number = get_number(False, os.path.basename(f))
    #     if n_number and n_number.lower() in skip_numbers:
    #         rm_list.append(f)
    # for f in rm_list:
    #     total.remove(f)
    #     if debug:
    #         print(
    #             f"[!]Skip file successfully processed within {nfo_skip_days} days: '{f}'")
    # if len(rm_list):
    #     print(
    #         f"[!]Skip {len(rm_list)} movies in success folder '{success_folder}' who's .nfo modified within {nfo_skip_days} days.")

    return total

# 删除空文件夹


def rm_empty_folder(path):
    abspath = os.path.abspath(path)
    deleted = set()
    for current_dir, subdirs, files in os.walk(abspath, topdown=False):
        try:
            still_has_subdirs = any(_ for subdir in subdirs if os.path.join(
                current_dir, subdir) not in deleted)
            if not any(files) and not still_has_subdirs and not os.path.samefile(path, current_dir):
                os.rmdir(current_dir)
                deleted.add(current_dir)
                print('[+]Deleting empty folder', current_dir)
        except:
            pass

# todo


def get_numbers(paths: List[str]) -> tuple[list[PathMeta], dict[str, list[PathMeta]]]:
    """提取对应路径的番号+集数,集数可能含C(中文字幕)但非分集"""

    def get_number(filepath: str, absolute_path=False):
        """
        获取番号，集数
        :param filepath:
        :param absolute_path:
        :return:
        """
        name = filepath.upper()  # 转大写
        if absolute_path:
            name = name.replace('\\', '/')
        # 1. 移除干扰字段
        name = PathNameProcessor.remove_distractions(name)
        # 2. 抽取文件路径中可能存在的尾部集数，和抽取尾部集数的后的文件路径
        episode_suffix, name = PathNameProcessor.extract_suffix_episode(name)
        # 3. 抽取 文件路径中可能存在的 番号后跟随的集数 和 处理后番号
        code_number, episode_behind_code, is_uncensored, is_cracked, is_leaked, is_cn_subs = PathNameProcessor.extract_code(
            name)
        # 优先取尾部集数，无则取番号后的集数（几率低）

        return PathMeta(path=filepath, code=code_number, possible_episodes=[episode_suffix, episode_behind_code], is_uncensored=is_uncensored, is_cracked=is_cracked, is_leaked=is_leaked, is_cn_subs=is_cn_subs)
        # return namedtuple('R', ['code', 'possible_episodes','is_uncensored','is_cracked','is_leaked', 'is_cn_subs'])(code_number,[episode_suffix,episode_behind_code],is_uncensored,is_cracked,is_leaked,is_cn_subs)

    # 如果是 JAV
    path_list = list(map((lambda x: get_number(x)), paths))

    paths_by_code = {k: list(v) for k, v in groupby(path_list, key=lambda x: x.code)}

    # 目的: 找出分集是C 但实际是中文字幕标志的情况: 如果同code时, episode 有C无B集时 ,则为中文字幕视频 并非episode,  那么另一个可能的episode 就是真正集数. 如果找不到,则优先取一个episode
    # 实际只修改了 episode 和 is_cn_subs
    for codeKey, itemList in paths_by_code.items():

        for i in itemList:

            if 'C' in i.possible_episodes:   # 如果不是中文字幕视频, 可能有的集数字段有‘C’ 才处理

                eps = copy.deepcopy(i.possible_episodes)
                # if G_ini_conf.Name_Rule.string_c_recognition_strategy == ConfigModel.NameRuleConfig.StringCRecognitionStrategy.auto:
                # 找到 CnSusbtile 位置
                if (index_Cn_Ep := pydash.find_index(eps, lambda ep: ep == 'C' and not pydash.find(itemList, lambda x: 'B' in x.possible_episodes))) > -1:
                    del eps[index_Cn_Ep]
                    i.is_cn_subs = True
                # 可能的分集参数, 按顺位取
                i.episode = eps[0] if len(eps) > 0 else None
                # elif G_ini_conf.Name_Rule.string_c_recognition_strategy == ConfigModel.NameRuleConfig.StringCRecognitionStrategy.part:
                #     i.episode = 'C'
                # elif G_ini_conf.Name_Rule.string_c_recognition_strategy == ConfigModel.NameRuleConfig.StringCRecognitionStrategy.cn:
                #     eps.remove('C')
                #     i.episode = eps[0] if len(eps) > 0 else None
                #     i.is_cn_subs = True

            else:
                i.episode = i.possible_episodes[0] if len(
                    i.possible_episodes) > 0 else None

    return namedtuple('R', ['path_list', 'paths_by_code'])(path_list, paths_by_code)
