# 程序入口
from collections import namedtuple
from itertools import groupby
from operator import itemgetter
from types import SimpleNamespace
import argparse
import json
import os
import random
import re
import sys
import time
import shutil
import typing
import pydash
import urllib3
import signal
import platform
from ConfigModel import ConfigModel
from PathNameProcessor import PathNameProcessor
import number_parser
import config

from config import Main_Mode
from datetime import datetime, timedelta
from lxml import etree
from pathlib import Path
from opencc import OpenCC

from scraper import get_data_from_json
from ADC_function import file_modification_days, get_html, parallel_download_files
from number_parser import get_number
from core import core_main, core_main_no_net_op, moveFailedFolder, debug_print


# 更新版本号
def check_update(local_version):
    htmlcode = get_html("https://api.github.com/repos/yoshiko2/Movie_Data_Capture/releases/latest")
    data = json.loads(htmlcode)
    remote = int(data["tag_name"].replace(".", ""))
    local_version = int(local_version.replace(".", ""))
    if local_version < remote:
        print("[*]" + ("* New update " + str(data["tag_name"]) + " *").center(54))
        print("[*]" + "↓ Download ↓".center(54))
        print("[*]https://github.com/yoshiko2/Movie_Data_Capture/releases")
        print("[*]======================================================")


def argparse_function(ver: str, conf: config.Config) -> typing.Tuple[str, str, str, str, bool, bool, str, str]:
    parser = argparse.ArgumentParser(epilog=f"Load Config file '{conf.ini_path}'.")
    parser.add_argument("file", default='', nargs='?', help="Single Movie file path.")
    parser.add_argument("-p", "--path", default='', nargs='?', help="Analysis folder path.")
    parser.add_argument("-m", "--main-mode", default='', nargs='?',
                        help="Main mode. 1:Scraping 2:Organizing 3:Scraping in analysis folder")
    parser.add_argument("-n", "--number", default='', nargs='?', help="Custom file number of single movie file.")
    # parser.add_argument("-C", "--config", default='config.ini', nargs='?', help="The config file Path.")
    parser.add_argument("-L", "--link-mode", default='', nargs='?',
                        help="Create movie file link. 0:moving movie file, do not create link 1:soft link 2:try hard link first")
    default_logdir = str(Path.home() / '.mlogs')
    parser.add_argument("-o", "--log-dir", dest='logdir', default=default_logdir, nargs='?',
                        help=f"""Duplicate stdout and stderr to logfiles in logging folder, default on.
        default folder for current user: '{default_logdir}'. Change default folder to an empty file,
        or use --log-dir= to turn log off.""")
    parser.add_argument("-q", "--regex-query", dest='regexstr', default='', nargs='?',
                        help="python re module regex filepath filtering.")
    parser.add_argument("-d", "--nfo-skip-days", dest='days', default='', nargs='?',
                        help="Override nfo_skip_days value in config.")
    parser.add_argument("-c", "--stop-counter", dest='cnt', default='', nargs='?',
                        help="Override stop_counter value in config.")
    parser.add_argument("-R", "--rerun-delay", dest='delaytm', default='', nargs='?',
                        help="Delay (eg. 1h10m30s or 60 (second)) time and rerun, until all movies proceed. Note: stop_counter value in config or -c must none zero.")
    parser.add_argument("-i", "--ignore-failed-list", action="store_true", help="Ignore failed list '{}'".format(
        os.path.join(os.path.abspath(conf.failed_folder()), 'failed_list.txt')))
    parser.add_argument("-a", "--auto-exit", action="store_true",
                        help="Auto exit after program complete")
    parser.add_argument("-g", "--debug", action="store_true",
                        help="Turn on debug mode to generate diagnostic log for issue report.")
    parser.add_argument("-N", "--no-network-operation", action="store_true",
                        help="No network query, do not get metadata, for cover cropping purposes, only takes effect when main mode is 3.")
    parser.add_argument("-w", "--website", dest='site', default='', nargs='?',
                        help="Override [priority]website= in config.")
    parser.add_argument("-D", "--download-images", dest='dnimg', action="store_true",
                        help="Override [common]download_only_missing_images=0 force invoke image downloading.")
    parser.add_argument("-C", "--config-override", dest='cfgcmd', action='append', nargs=1,
                        help="Common use config override. Grammar: section:key=value[;[section:]key=value] eg. 'de:s=1' or 'debug_mode:switch=1' override[debug_mode]switch=1 Note:this parameters can be used multiple times")
    parser.add_argument("-z", "--zero-operation", dest='zero_op', action="store_true",
                        help="""Only show job list of files and numbers, and **NO** actual operation
is performed. It may help you correct wrong numbers before real job.""")
    parser.add_argument("-v", "--version", action="version", version=ver)
    parser.add_argument("-s", "--search", default='', nargs='?', help="Search number")
    parser.add_argument("-ss", "--specified-source", default='', nargs='?', help="specified Source.")
    parser.add_argument("-su", "--specified-url", default='', nargs='?', help="specified Url.")

    args = parser.parse_args()

    def set_natural_number_or_none(sk, value):
        if isinstance(value, str) and value.isnumeric() and int(value) >= 0:
            conf.set_override(f'{sk}={value}')

    def set_str_or_none(sk, value):
        if isinstance(value, str) and len(value):
            conf.set_override(f'{sk}={value}')

    def set_bool_or_none(sk, value):
        if isinstance(value, bool) and value:
            conf.set_override(f'{sk}=1')

    set_natural_number_or_none("common:main_mode", args.main_mode)
    set_natural_number_or_none("common:link_mode", args.link_mode)
    set_str_or_none("common:source_folder", args.path)
    set_bool_or_none("common:auto_exit", args.auto_exit)
    set_natural_number_or_none("common:nfo_skip_days", args.days)
    set_natural_number_or_none("advenced_sleep:stop_counter", args.cnt)
    set_bool_or_none("common:ignore_failed_list", args.ignore_failed_list)
    set_str_or_none("advenced_sleep:rerun_delay", args.delaytm)
    set_str_or_none("priority:website", args.site)
    if isinstance(args.dnimg, bool) and args.dnimg:
        conf.set_override("common:download_only_missing_images=0")
    set_bool_or_none("debug_mode:switch", args.debug)
    if isinstance(args.cfgcmd, list):
        for cmd in args.cfgcmd:
            conf.set_override(cmd[0])

    no_net_op = False
    if conf.main_mode() == config.Main_Mode.ScrapingInAnalysisFolder:
        no_net_op = args.no_network_operation
        if no_net_op:
            conf.set_override("advenced_sleep:stop_counter=0;advenced_sleep:rerun_delay=0s;face:aways_imagecut=1")

    return args.file, args.number, args.logdir, args.regexstr, args.zero_op, no_net_op, args.search, args.specified_source, args.specified_url


class OutLogger(object):
    def __init__(self, logfile) -> None:
        self.term = sys.stdout
        self.log = open(logfile, "w", encoding='utf-8', buffering=1)
        self.filepath = logfile

    def __del__(self):
        self.close()

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.close()

    def write(self, msg):
        self.term.write(msg)
        self.log.write(msg)

    def flush(self):
        if 'flush' in dir(self.term):
            self.term.flush()
        if 'flush' in dir(self.log):
            self.log.flush()
        if 'fileno' in dir(self.log):
            os.fsync(self.log.fileno())

    def close(self):
        if self.term is not None:
            sys.stdout = self.term
            self.term = None
        if self.log is not None:
            self.log.close()
            self.log = None


class ErrLogger(OutLogger):

    def __init__(self, logfile) -> None:
        self.term = sys.stderr
        self.log = open(logfile, "w", encoding='utf-8', buffering=1)
        self.filepath = logfile

    def close(self):
        if self.term is not None:
            sys.stderr = self.term
            self.term = None

        if self.log is not None:
            self.log.close()
            self.log = None


def dupe_stdout_to_logfile(logdir: str):
    if not isinstance(logdir, str) or len(logdir) == 0:
        return
    log_dir = Path(logdir)
    if not log_dir.exists():
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except:
            pass
    if not log_dir.is_dir():
        return  # Tips for disabling logs by change directory to a same name empty regular file
    abslog_dir = log_dir.resolve()
    log_tmstr = datetime.now().strftime("%Y%m%dT%H%M%S")
    logfile = abslog_dir / f'mdc_{log_tmstr}.txt'
    errlog = abslog_dir / f'mdc_{log_tmstr}_err.txt'

    sys.stdout = OutLogger(logfile)
    sys.stderr = ErrLogger(errlog)


def close_logfile(logdir: str):
    if not isinstance(logdir, str) or len(logdir) == 0 or not os.path.isdir(logdir):
        return
    # 日志关闭前保存日志路径
    filepath = None
    try:
        filepath = sys.stdout.filepath
    except:
        pass
    sys.stdout.close()
    sys.stderr.close()
    log_dir = Path(logdir).resolve()
    if isinstance(filepath, Path):
        print(f"Log file '{filepath}' saved.")
        assert (filepath.parent.samefile(log_dir))
    # 清理空文件
    for f in log_dir.glob(r'*_err.txt'):
        if f.stat().st_size == 0:
            try:
                f.unlink(missing_ok=True)
            except:
                pass
    # 合并日志 只检测日志目录内的文本日志，忽略子目录。三天前的日志，按日合并为单个日志，三个月前的日志，
    # 按月合并为单个月志，去年及以前的月志，今年4月以后将之按年合并为年志
    # 测试步骤：
    """
    LOGDIR=/tmp/mlog
    mkdir -p $LOGDIR
    for f in {2016..2020}{01..12}{01..28};do;echo $f>$LOGDIR/mdc_${f}T235959.txt;done
    for f in {01..09}{01..28};do;echo 2021$f>$LOGDIR/mdc_2021${f}T235959.txt;done
    for f in {00..23};do;echo 20211001T$f>$LOGDIR/mdc_20211001T${f}5959.txt;done
    echo "$(ls -1 $LOGDIR|wc -l) files in $LOGDIR"
    # 1932 files in /tmp/mlog
    mdc -zgic1 -d0 -m3 -o $LOGDIR
    # python3 ./__init__.py -zgic1 -o $LOGDIR
    ls $LOGDIR
    # rm -rf $LOGDIR
    """
    today = datetime.today()
    # 第一步，合并到日。3天前的日志，文件名是同一天的合并为一份日志
    for i in range(1):
        txts = [f for f in log_dir.glob(r'*.txt') if re.match(r'^mdc_\d{8}T\d{6}$', f.stem, re.A)]
        if not txts or not len(txts):
            break
        e = [f for f in txts if '_err' in f.stem]
        txts.sort()
        tmstr_3_days_ago = (today.replace(hour=0) - timedelta(days=3)).strftime("%Y%m%dT99")
        deadline_day = f'mdc_{tmstr_3_days_ago}'
        day_merge = [f for f in txts if f.stem < deadline_day]
        if not day_merge or not len(day_merge):
            break
        cutday = len('T235959.txt')  # cut length mdc_20201201|T235959.txt
        for f in day_merge:
            try:
                day_file_name = str(f)[:-cutday] + '.txt'  # mdc_20201201.txt
                with open(day_file_name, 'a', encoding='utf-8') as m:
                    m.write(f.read_text(encoding='utf-8'))
                f.unlink(missing_ok=True)
            except:
                pass
    # 第二步，合并到月
    for i in range(1):  # 利用1次循环的break跳到第二步，避免大块if缩进或者使用goto语法
        txts = [f for f in log_dir.glob(r'*.txt') if re.match(r'^mdc_\d{8}$', f.stem, re.A)]
        if not txts or not len(txts):
            break
        txts.sort()
        tmstr_3_month_ago = (today.replace(day=1) - timedelta(days=3 * 30)).strftime("%Y%m32")
        deadline_month = f'mdc_{tmstr_3_month_ago}'
        month_merge = [f for f in txts if f.stem < deadline_month]
        if not month_merge or not len(month_merge):
            break
        tomonth = len('01.txt')  # cut length mdc_202012|01.txt
        for f in month_merge:
            try:
                month_file_name = str(f)[:-tomonth] + '.txt'  # mdc_202012.txt
                with open(month_file_name, 'a', encoding='utf-8') as m:
                    m.write(f.read_text(encoding='utf-8'))
                f.unlink(missing_ok=True)
            except:
                pass
    # 第三步，月合并到年
    for i in range(1):
        if today.month < 4:
            break
        mons = [f for f in log_dir.glob(r'*.txt') if re.match(r'^mdc_\d{6}$', f.stem, re.A)]
        if not mons or not len(mons):
            break
        mons.sort()
        deadline_year = f'mdc_{today.year - 1}13'
        year_merge = [f for f in mons if f.stem < deadline_year]
        if not year_merge or not len(year_merge):
            break
        toyear = len('12.txt')  # cut length mdc_2020|12.txt
        for f in year_merge:
            try:
                year_file_name = str(f)[:-toyear] + '.txt'  # mdc_2020.txt
                with open(year_file_name, 'a', encoding='utf-8') as y:
                    y.write(f.read_text(encoding='utf-8'))
                f.unlink(missing_ok=True)
            except:
                pass
    # 第四步，压缩年志 如果有压缩需求，请自行手工压缩，或者使用外部脚本来定时完成。推荐nongnu的lzip，对于
    # 这种粒度的文本日志，压缩比是目前最好的。lzip -9的运行参数下，日志压缩比要高于xz -9，而且内存占用更少，
    # 多核利用率更高(plzip多线程版本)，解压速度更快。压缩后的大小差不多是未压缩时的2.4%到3.7%左右，
    # 100MB的日志文件能缩小到3.7MB。
    return filepath


# 退出程序
def signal_handler(*args):
    print('[!]Ctrl+C detected, Exit.')
    os._exit(9)


# 调试模式开关
def sigdebug_handler(*args):
    conf = config.getInstance()
    conf.set_override(f"debug_mode:switch={int(not conf.debug())}")
    print(f"[!]Debug {('oFF', 'On')[int(conf.debug())]}")


# 获取待处理文件列表: 会按配置规则过滤不相关文件,新增失败文件列表跳过处理，及.nfo修改天数跳过处理，提示跳过视频总数，调试模式(-g)下详细被跳过文件，跳过小广告
def movie_lists(source_folder, regexstr: str) -> typing.List[str]:
    debug = G_conf.debug()
    nfo_skip_days = G_conf.nfo_skip_days()
    link_mode = G_conf.link_mode()
    file_type = G_conf.media_type().lower().split(",")
    trailerRE = re.compile(r'-trailer\.', re.IGNORECASE)
    cliRE = re.compile(regexstr, re.IGNORECASE)  if isinstance(regexstr, str) and len(regexstr) else None
    failed_list_txt_path = Path(G_conf.failed_folder()).resolve() / 'failed_list.txt'
    # 提取历史刮削失败的路径
    failed_set = set()
    if (G_conf.main_mode() == Main_Mode.ScrapingInAnalysisFolder or link_mode) and not G_conf.ignore_failed_list():
        try:
            flist = failed_list_txt_path.read_text(encoding='utf-8').splitlines()
            failed_set = set(flist)
            if len(flist) != len(failed_set):  # 检查去重并写回，但是不改变failed_list.txt内条目的先后次序，重复的只保留最后的
                fset = failed_set.copy()
                for i in range(len(flist) - 1, -1, -1):
                    fset.remove(flist[i]) if flist[i] in fset else flist.pop(i)
                failed_list_txt_path.write_text('\n'.join(flist) + '\n', encoding='utf-8')
                assert len(fset) == 0 and len(flist) == len(failed_set)
        except:
            pass
    if not Path(source_folder).is_dir():
        print('[-]Source folder not found!')
        return []
    total = []
    source = Path(source_folder).resolve()
    skip_failed_cnt, skip_nfo_days_cnt = 0, 0
    escape_folder_set = set(re.split("[,，]", G_conf.escape_folder()))
    # 遍历文件夹
    for full_name in source.glob(r'**/*'):
        # 原路径刮削
        if G_conf.main_mode() != Main_Mode.ScrapingInAnalysisFolder and set(full_name.parent.parts) & escape_folder_set:
            continue
        # 不是文件
        if not full_name.is_file():
            continue
        # 不是指定类型
        if not full_name.suffix.lower() in file_type:
            continue
        absf = str(full_name)
        if absf in failed_set:
            skip_failed_cnt += 1
            if debug:
                print('[!]Skip failed movie:', absf)
            continue
        is_sym = full_name.is_symlink()
        if G_conf.main_mode() != Main_Mode.ScrapingInAnalysisFolder and (is_sym or (
                full_name.stat().st_nlink > 1 and not G_conf.scan_hardlink())):  # 短路布尔 符号链接不取stat()，因为符号链接可能指向不存在目标
            continue  # 模式不等于3下跳过软连接和未配置硬链接刮削 
        # 调试用0字节样本允许通过，去除小于120MB的广告'苍老师强力推荐.mp4'(102.2MB)'黑道总裁.mp4'(98.4MB)'有趣的妹子激情表演.MP4'(95MB)'有趣的臺灣妹妹直播.mp4'(15.1MB)
        movie_size = 0 if is_sym else full_name.stat().st_size  # 同上 符号链接不取stat()及st_size，直接赋0跳过小视频检测
        # if 0 < movie_size < 125829120:  # 1024*1024*120=125829120
        #     continue
        if cliRE and not cliRE.search(absf) or trailerRE.search(full_name.name):
            continue
        if G_conf.main_mode() == Main_Mode.ScrapingInAnalysisFolder:
            nfo = full_name.with_suffix('.nfo')
            if not nfo.is_file():
                if debug:
                    print(f"[!]Metadata {nfo.name} not found for '{absf}'")
            elif nfo_skip_days > 0 and file_modification_days(nfo) <= nfo_skip_days:
                skip_nfo_days_cnt += 1
                if debug:
                    print(f"[!]Skip movie by it's .nfo which modified within {nfo_skip_days} days: '{absf}'")
                continue
        total.append(absf)

    if skip_failed_cnt:
        print(f"[!]Skip {skip_failed_cnt} movies in failed list '{failed_list_txt_path}'.")
    if skip_nfo_days_cnt:
        print(
            f"[!]Skip {skip_nfo_days_cnt} movies in source folder '{source}' who's .nfo modified within {nfo_skip_days} days.")
    if nfo_skip_days <= 0 or not link_mode or G_conf.main_mode() == Main_Mode.ScrapingInAnalysisFolder:
        return total
    # 软连接方式，已经成功削刮的也需要从成功目录中检查.nfo更新天数，跳过N天内更新过的
    skip_numbers = set()
    success_folder = Path(G_conf.success_folder()).resolve()
    for f in success_folder.glob(r'**/*'):
        if not re.match(r'\.nfo$', f.suffix, re.IGNORECASE):
            continue
        if file_modification_days(f) > nfo_skip_days:
            continue
        number = get_number(False, f.stem)
        if not number:
            continue
        skip_numbers.add(number.lower())

    rm_list = []
    for f in total:
        n_number = get_number(False, os.path.basename(f))
        if n_number and n_number.lower() in skip_numbers:
            rm_list.append(f)
    for f in rm_list:
        total.remove(f)
        if debug:
            print(f"[!]Skip file successfully processed within {nfo_skip_days} days: '{f}'")
    if len(rm_list):
        print(
            f"[!]Skip {len(rm_list)} movies in success folder '{success_folder}' who's .nfo modified within {nfo_skip_days} days.")

    return total


# 生成失败文件夹
def create_failed_folder(failed_folder: str):
    """
    新建failed文件夹
    """
    if not os.path.exists(failed_folder):
        try:
            os.makedirs(failed_folder)
        except:
            print(f"[-]Fatal error! Can not make folder '{failed_folder}'")
            os._exit(0)


# 删除空文件夹
def rm_empty_folder(path):
    abspath = os.path.abspath(path)
    deleted = set()
    for current_dir, subdirs, files in os.walk(abspath, topdown=False):
        try:
            still_has_subdirs = any(_ for subdir in subdirs if os.path.join(current_dir, subdir) not in deleted)
            if not any(files) and not still_has_subdirs and not os.path.samefile(path, current_dir):
                os.rmdir(current_dir)
                deleted.add(current_dir)
                print('[+]Deleting empty folder', current_dir)
        except:
            pass


def get_numbers(paths: typing.List[str]):
    """提取对应路径的番号+集数,集数可能含C(中文字幕)但非分集"""

    def get_number(filepath, absolute_path=False):
        """
        获取番号，集数
        :param filepath:
        :param absolute_path:
        :return:
        """
        name = filepath.upper()  # 转大写
        if absolute_path:
            name = name.replace('\\', '/')
        # 移除干扰字段
        name = PathNameProcessor.remove_distractions(name)
        # 抽取 文件路径中可能存在的尾部集数，和抽取尾部集数的后的文件路径
        suffix_episode, name = PathNameProcessor.extract_suffix_episode(name)
        # 抽取 文件路径中可能存在的 番号后跟随的集数 和 处理后番号
        code_number, episode_behind_code = PathNameProcessor.extract_code(name)
        # 无番号 则设置空字符
        code_number = code_number if code_number else ''
        # 优先取尾部集数，无则取番号后的集数（几率低），都无则为空字符
        episode = suffix_episode or episode_behind_code or None

        # return namedtuple('R', ['code', 'episode'])(code_number,episode) 
        return SimpleNamespace(code=code_number, episode=episode, isCn=False)

    # paths 按 code_number 分组 为新字典
    if G_ini_conf.common.movie_type == 1:
        path_list = list(map((lambda x: SimpleNamespace(path=x, result=get_number(x))), paths))
    else:
        path_list = list(map((lambda x: SimpleNamespace(path=x, result=number_parser.get_number_tp(x))), paths))
    grouped_data = {k: list(v) for k, v in groupby(path_list, key=lambda x: x.result.code)}

    # 处理: 如果同code时, episode 有c无b,a ,则为中文字幕视频 并非episode
    for codeKey, itemList in grouped_data.items():
        for i in itemList:
            if (
                    (ep := i.result.episode) and
                    ep is not None and ep.lower() == 'c' and
                    not pydash.find(itemList, lambda x: (x.result.episode or '').lower() in ['a', 'b'])
            ):
                i.result.episode = None
                i.result.isCn = True
            else:
                continue

    return path_list


# 生成数据并移动
def create_data_and_move(movie_path: str, zero_op: bool, no_net_op: bool, oCC):
    """
生成数据并移动
    :param movie_path:路径
    :param zero_op:是否为 不操作
    :param no_net_op:是否为 无网络操作

    """
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    debug = config.getInstance().debug()
    # 如果配置项 test_movie_list 
    # ❤️获取番号核心处理❤️  
    n_number = get_number(debug, os.path.basename(movie_path))
    movie_path = os.path.abspath(movie_path)

    if debug is True:
        print(f"[!] [{n_number}] As Number Processing for '{movie_path}'")
        if zero_op:
            return
        if n_number:
            if no_net_op:
                core_main_no_net_op(movie_path, n_number)
            else:
                core_main(movie_path, n_number, oCC)
        else:
            print("[-] number empty ERROR")
            moveFailedFolder(movie_path)
        print("[*]======================================================")
    else:
        try:
            print(f"[!] [{n_number}] As Number Processing for '{movie_path}'")
            if zero_op:
                # zero operation 大概是 不操作的意思吧...
                return
            if n_number:
                if no_net_op:
                    core_main_no_net_op(movie_path, n_number)
                else:
                    # 核心❤️
                    core_main(movie_path, n_number, oCC)
            else:
                raise ValueError("number empty")
            print("[*]======================================================")
        except Exception as err:
            print(f"[-] [{movie_path}] ERROR:")
            print('[-]', err)

            try:
                moveFailedFolder(movie_path)
            except Exception as err:
                print('[!]', err)


def create_data_and_move_with_custom_number(file_path: str, custom_number, oCC, specified_source, specified_url):
    conf = config.getInstance()
    file_name = os.path.basename(file_path)
    try:
        print("[!] [{1}] As Number Processing for '{0}'".format(file_path, custom_number))
        if custom_number:
            core_main(file_path, custom_number, oCC, specified_source, specified_url)
        else:
            print("[-] number empty ERROR")
        print("[*]======================================================")
    except Exception as err:
        print("[-] [{}] ERROR:".format(file_path))
        print('[-]', err)

        if conf.link_mode():
            print("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, os.path.join(conf.failed_folder(), file_name))
        else:
            try:
                print("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, os.path.join(conf.failed_folder(), file_name))
            except Exception as err:
                print('[!]', err)


# 开始处理 启动的入口 ❤️
def main(args: tuple) -> Path:
    # 获取配置 zero_op 是否为 不操作:只获取番号, no_net_op  离线操作(不联网)
    (single_file_path, custom_number, logdir, regexstr, zero_op, no_net_op, search, specified_source,
     specified_url) = args

    folder_path = ""

    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform == 'win32':
        signal.signal(signal.SIGBREAK, sigdebug_handler)
    else:
        signal.signal(signal.SIGWINCH, sigdebug_handler)
    dupe_stdout_to_logfile(logdir)

    platform_total = str(
        ' - ' + platform.platform() + ' \n[*] - ' + platform.machine() + ' - Python-' + platform.python_version())

    print('[*]================= Movie Data Capture =================')
    print('[*]' + version.center(54))
    print('[*]======================================================')
    print('[*]' + platform_total)
    print('[*]======================================================')
    print('[*] - 严禁在墙内宣传本项目 - ')
    print('[*]======================================================')

    start_time = time.time()
    print('[+]Start at', time.strftime("%Y-%m-%d %H:%M:%S"))

    print(f"[+]Load Config file '{G_conf.ini_path}'.")
    if G_conf.debug():
        print('[+]Enable debug')
    if G_conf.link_mode() in (1, 2):
        print('[!]Enable {} link'.format(('soft', 'hard')[G_conf.link_mode() - 1]))
    if len(sys.argv) > 1:
        print('[!]CmdLine:', " ".join(sys.argv[1:]))
    print('[+]Main Working mode ## {}: {} ## {}{}{}'
          .format(*(G_conf.main_mode().value, G_conf.main_mode().name,
                    "" if not G_conf.multi_threading() else ", multi_threading on",
                    "" if G_conf.nfo_skip_days() == 0 else f", nfo_skip_days={G_conf.nfo_skip_days()}",
                    "" if G_conf.stop_counter() == 0 else f", stop_counter={G_conf.stop_counter()}"
                    ) if not single_file_path else ('-', 'Single File', '', '', ''))
          )
    # 更新检查
    if G_conf.update_check():
        try:
            check_update(version)

            # Download Mapping Table, parallel version
            def fmd(f) -> typing.Tuple[str, Path]:
                return ('https://raw.githubusercontent.com/yoshiko2/Movie_Data_Capture/master/MappingTable/' + f,
                        Path.home() / '.local' / 'share' / 'mdc' / f)

            map_tab = (fmd('mapping_actor.xml'), fmd('mapping_info.xml'), fmd('c_number.json'))
            for k, v in map_tab:
                if v.exists():
                    if file_modification_days(str(v)) >= G_conf.mapping_table_validity():
                        print("[+]Mapping Table Out of date! Remove", str(v))
                        os.remove(str(v))
            res = parallel_download_files(((k, v) for k, v in map_tab if not v.exists()))
            for i, fp in enumerate(res, start=1):
                if fp and len(fp):
                    print(f"[+] [{i}/{len(res)}] Mapping Table Downloaded to {fp}")
                else:
                    print(f"[-] [{i}/{len(res)}] Mapping Table Download failed")
        except:
            print("[!]" + " WARNING ".center(54, "="))
            print('[!]' + '-- GITHUB CONNECTION FAILED --'.center(54))
            print('[!]' + 'Failed to check for updates'.center(54))
            print('[!]' + '& update the mapping table'.center(54))
            print("[!]" + "".center(54, "="))
            try:
                etree.parse(str(Path.home() / '.local' / 'share' / 'mdc' / 'mapping_actor.xml'))
            except:
                print('[!]' + "Failed to load mapping table".center(54))
                print('[!]' + "".center(54, "="))
    # 创建处理失败文件夹
    create_failed_folder(G_conf.failed_folder())

    # create OpenCC converter
    ccm = G_conf.cc_convert_mode()
    # 0: no convert, 1: t2s, 2: s2t
    try:
        oCC = None if ccm == 0 else OpenCC('t2s.json' if ccm == 1 else 's2t.json')
    except:
        # some OS no OpenCC cpython, try opencc-python-reimplemented.
        # pip uninstall opencc && pip install opencc-python-reimplemented
        oCC = None if ccm == 0 else OpenCC('t2s' if ccm == 1 else 's2t')
    # 搜索模式
    if not search == '':
        search_list = search.split(",")
        for i in search_list:
            json_data = get_data_from_json(i, oCC, None, None)
            debug_print(json_data)
            time.sleep(int(config.getInstance().sleep()))
        os._exit(0)
    # 单文件处理
    if not single_file_path == '':  # Single File
        print('[+]==================== Single File =====================')
        if custom_number == '':
            create_data_and_move_with_custom_number(single_file_path,
                                                    get_number(G_conf.debug(), os.path.basename(single_file_path)), oCC,
                                                    specified_source, specified_url)
        else:
            create_data_and_move_with_custom_number(single_file_path, custom_number, oCC,
                                                    specified_source, specified_url)
    else:
        # 文件夹处理
        folder_path = G_conf.source_folder()
        if not isinstance(folder_path, str) or folder_path == '':
            folder_path = os.path.abspath("..")

        # 读取 测试文件里的电影路径 或 文件夹下的所有文件
        def _get_movie_list():
            if (test_movie_list_path := G_ini_conf.common.test_movie_list) and os.path.isfile(test_movie_list_path):
                return [line.strip() for line in open(test_movie_list_path, encoding='utf-8') if line.strip()]
            else:
                return movie_lists(folder_path, regexstr)

        movie_list = _get_movie_list()
        code_ep_paths = get_numbers(movie_list)
        print('| 根据路径文件名识别的番号信息,请确认识别的信息无误')
        [print('|', i.path, '\n|    ','|📟', i.result.code,'📟|📚',i.result.episode,'📚|💬🇨🇳',i.result.isCn) for i in code_ep_paths]
        print('|======================================================')


        count = 0
        count_all = str(len(movie_list))
        print('[+]Find', count_all, 'movies.', 'main_mode:', G_ini_conf.common.main_mode.name)
        print('[*]======================================================')

        # 终端输出 '是否继续?, y 或者 enter 案件继续,其他键退出'
        if not input('[?]继续? ( ‘y’或者直接回车继续, 其他任意案件退出): ') in ('', 'y'):
            print('[!]Exit.')
            os._exit(0)

        # 获取停止计数,用于限制连续处理的文件数量
        stop_count = G_conf.stop_counter()
        if stop_count < 1:
            stop_count = 999999
        else:
            count_all = str(min(len(movie_list), stop_count))
        # 先获取遍历电影列表,提取不联网的影片信息, 比如: 分集,是否内嵌中文,是否泄漏版,是否去马赛克版

        for movie_path in movie_list:  # 遍历电影列表 交给core处理
            count = count + 1
            percentage = str(count / int(count_all) * 100)[:4] + '%'
            print('[!] {:>30}{:>21}'.format('- ' + percentage + ' [' + str(count) + '/' + count_all + '] -',
                                            time.strftime("%H:%M:%S")))
            # ❤️ 核心处理逻辑 ❤️
            create_data_and_move(movie_path, zero_op, no_net_op, oCC)
            # 如果停止计数大于0,并且已经处理的文件数量大于等于停止计数,则退出循环,等待下次启动
            if count >= stop_count:
                print("[!]Stop counter triggered!")
                break
            sleep_seconds = random.randint(G_conf.sleep(), G_conf.sleep() + 2)
            time.sleep(sleep_seconds)

    if G_conf.del_empty_folder() and not zero_op:
        rm_empty_folder(G_conf.success_folder())
        rm_empty_folder(G_conf.failed_folder())
        if len(folder_path):
            rm_empty_folder(folder_path)

    end_time = time.time()
    total_time = str(timedelta(seconds=end_time - start_time))
    print("[+]Running time", total_time[:len(total_time) if total_time.rfind('.') < 0 else -3],
          " End at", time.strftime("%Y-%m-%d %H:%M:%S"))

    print("[+]All finished!!!")

    return close_logfile(logdir)


# 从日志获取 处理后的结果
def getResultNumbers(logfile):
    """ 从日志获取 处理后的结果 
    :param logfile: 日志文件
    :return: 扫描数，处理数，成功数
    """
    try:
        if not (isinstance(logfile, Path) and logfile.is_file()):
            raise FileNotFoundError('log file not found')
        logtxt = logfile.read_text(encoding='utf-8')
        numberOfScaned = int(re.findall(r'\[\+]Find (.*) movies\.', logtxt)[0])
        numberOfProcessed = int(re.findall(r'\[1/(.*?)] -', logtxt)[0])
        numberOfSuccess = logtxt.count(r'[+]Wrote!')
        return numberOfScaned, numberOfProcessed, numberOfSuccess
    except:
        return None, None, None


# 日期转换
def period(delta, pattern):
    d = {'d': delta.days}
    d['h'], rem = divmod(delta.seconds, 3600)
    d['m'], d['s'] = divmod(rem, 60)
    return pattern.format(**d)


# 首先读取配置文件的配置，然后读取命令行的配置，最后读取环境变量的配置
G_conf = config.getInstance()
global G_ini_conf
G_ini_conf = ConfigModel.get_config(Path.cwd() / "MDC/config.ini")
# 代码入口
if __name__ == '__main__':
    version = '6.6.7'
    urllib3.disable_warnings()  # Ignore http proxy warning
    app_start_time = time.time()

    # Parse command line args and override config.ini
    args = tuple(argparse_function(version, G_conf))

    # 高级睡眠模式: 自动周期运行
    # 间隔时间大于0 且 停止计数大于0
    interval = G_ini_conf.advenced_sleep.rerun_delay  # G_conf.rerun_delay()

    if interval > 0 and G_ini_conf.advenced_sleep.stop_counter > 0:
        while True:
            try:
                # 开始处理 ❤️
                logfile = main(args)
                (numberOfScaned, numberOfProcessed, numberOfSuccess) = resultTuple = tuple(getResultNumbers(logfile))
                if all(isinstance(v, int) for v in resultTuple):
                    # 未处理的个数
                    numberOfNotProcessed = numberOfScaned - numberOfProcessed
                    # 处理用时
                    processTime = timedelta(seconds=time.time() - app_start_time)
                    print(
                        f'All movies:{numberOfScaned}  processed:{numberOfProcessed}  successes:{numberOfSuccess}  remain:{numberOfNotProcessed}' +
                        '  Elapsed time {}'.format(
                            period(processTime, "{d} day {h}:{m:02}:{s:02}") if processTime.days == 1
                            else period(processTime, "{d} days {h}:{m:02}:{s:02}") if processTime.days > 1
                            else period(processTime, "{h}:{m:02}:{s:02}")))
                    if numberOfNotProcessed == 0:
                        break
                    dateOfNextRun = datetime.now() + timedelta(seconds=interval)
                    print(
                        f'Next run time: {dateOfNextRun.strftime("%H:%M:%S")}, rerun_delay={interval}, press Ctrl+C stop run.')
                    time.sleep(interval)
                else:
                    break
            except:
                break
    else:
        # 普通模式: 运行一次
        # 开始处理
        main(args)

    if not G_ini_conf.common.auto_exit:
        if sys.platform == 'win32':
            input("Press enter key exit, you can check the error message before you exit...")
