# 把 source 目录下的子目录的所有 视频文件(.mp4,.avi,.rmvb,.wmv,.mov,.mkv,.flv,.ts,.webm,.iso,.mpg,.m4v) 数量合计不超过3个 都 移动 到 target 目录下,
# 1. 先列出文件夹: 文件夹内视频文件不超过3个的文件夹
# 2. 回车Y 才开始移动
# 3. 移动时 把文件夹中所有文件都移动target 目录下.
# 4. 如果移动后的文件名相同,则重命名文件: '原文件名' + '-alt' 如果依然相同则 再加  '-alt' , 原后缀不变
# 4. 移动后删除 空文件夹

import os
import shutil


def is_video_file(filename):
    video_extensions = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov',
                        '.mkv', '.flv', '.ts', '.webm', '.iso', '.mpg', '.m4v']
    return any(filename.lower().endswith(ext) for ext in video_extensions)


def list_dirs_with_few_videos(source_dir, whitelist):
    eligible_dirs = []
    for root, dirs, files in os.walk(source_dir):
        # 跳过包含白名单词汇的目录
        if any(whitelisted_word in root for whitelisted_word in whitelist):
            continue
        video_files = [file for file in files if is_video_file(file)]
        if 0 < len(video_files) <= 3:
            eligible_dirs.append(root)
    return eligible_dirs


def move_files(source_dir, target_dir, directories):
    for dir in directories:
        for root, _, files in os.walk(dir):
            for file in files:
                source_path = os.path.join(root, file)
                target_path = os.path.join(target_dir, file)
                # Handle file name conflict and length limit
                original_target_path = target_path
                while os.path.exists(target_path) and len(target_path) <= 255:
                    name, ext = os.path.splitext(target_path)
                    target_path = f"{name}-alt{ext}"
                if len(target_path) > 255:
                    print(f"文件名过长，将直接覆盖：{original_target_path}")
                    target_path = original_target_path  # Reset to original to overwrite
                shutil.move(source_path, target_path)
            # Remove empty directories
            if not os.listdir(root):
                os.rmdir(root)


def main(source_dir, target_dir, whitelist):
    dirs_with_few_videos = list_dirs_with_few_videos(source_dir, whitelist)
    print("以下文件夹包含不超过3个视频文件:")
    for dir in dirs_with_few_videos:
        print(dir)

    confirm = input("确认移动这些文件夹中的所有文件到目标目录？(Y/n): ")
    if confirm.lower() == 'y':
        move_files(source_dir, target_dir, dirs_with_few_videos)
        print("文件已成功移动。")
    else:
        print("操作已取消。")

# 示例使用方式，将以下路径替换为实际的路径
# main('/path/to/source', '/path/to/target')


# 使用示例
# 白名单的
whitelist = ['已刮', '已处理']

main('/mnt/dsm/volume5/v3/Japan/oganized',
     '/mnt/dsm/volume5/v3/Japan/others', whitelist)
