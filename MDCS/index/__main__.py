
import os
from helper.global_config import config
from .path_index import movie_lists, get_numbers


def main():
    if config.index.is_disabled == True:
        return

    # 文件夹处理
    folder_path = config.index.source_dir
    if not isinstance(folder_path, str) or folder_path == '':
        folder_path = os.path.abspath("..")

    # FIXME 读取 测试文件里的电影路径 或 文件夹下的所有文件
    def _get_movie_list():

        if (test_movie_list_path := config.test.simulate_file_list_path) and os.path.isfile(test_movie_list_path):
            return [line.strip() for line in open(test_movie_list_path, encoding='utf-8') if line.strip()]
        else:

            return movie_lists(folder_path, '')

    movie_list = _get_movie_list()

    code_ep_paths, paths_by_code = get_numbers(movie_list)
    print('| 根据路径文件名识别的番号信息,请确认识别的信息无误')

    [print(f'|{i.path}\n|=====📟{i.code} 📚{i.episode} ({"💬" if i.is_cn_subs else ""}{"🚰" if i.is_leaked else ""}{"🛠️" if i.is_cracked else ""}{"🈚" if i.is_uncensored else ""} )') for i in code_ep_paths]
    print('|======================================================')

    count = 0
    count_all = str(len(movie_list))
    print('[+]Find', count_all, 'movies.')
    print('[*]======================================================')

    # 终端输出 '是否继续?, y 或者 enter 案件继续,其他键退出'
    if not input('[?]继续? ( ‘y’或者直接回车继续, 其他任意案件退出): ') in ('', 'y'):
        print('[!]Exit.')
        os._exit(0)

    # 获取停止计数,用于限制连续处理的文件数量
    # stop_count = G_conf.stop_counter()
    # if stop_count < 1:
    #     stop_count = 999999
    # else:
    #     count_all = str(min(len(movie_list), stop_count))
    # 先获取遍历电影列表,提取不联网的影片信息, 比如: 分集,是否内嵌中文,是否泄漏版,是否去马赛克版

    #
    # 如果是 JAV 使用 JAV定制逻辑, 识别信息 准确率会更高
    # for code, paths in paths_by_code.items():
    #     media_data_generate.generate(
    #         code, paths, oCC, specified_source, specified_url)
