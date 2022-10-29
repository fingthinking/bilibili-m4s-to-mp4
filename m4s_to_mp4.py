#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: motu
@time:   2022/10/29 上午11:59
"""

import sys
import getopt
import os
import subprocess
import json
import time


def panic(msg):
    print("程序执行错误: msg={}".format(msg))
    exit(1)


def process_args(args):
    """
    处理用户参数输入
    :return:
    """
    msg = """
    描述: bilibili缓存m4s文件转mp4工具
    
    相关参数:
        -h, --help              展示当前说明
        -i, --input             [必须]视频合集所属文件夹或其父目录, 请务必包含entry.json文件
        -o, --output            [非必须]默认input同名目录下创建output-{timestamp}文件夹
        -p, --processor         [非必须]开启的进程数, 最多允许多少个进程同时执行转码    
            --ffmpeg            [非必须]ffmpeg文件所在位置, 非必须字段, 优先从which ffmpeg查找
    """
    short_arg = "hi:o:"
    long_arg = ["help", "input=", "output=", "ffmpeg="]
    # 解析的opts及剩余的args
    opts, args = getopt.getopt(args, short_arg, long_arg)
    inputs = []
    outputs = []
    input_output = []
    ffmpeg = None
    for opt_name, opt_value in opts:
        if opt_name in ("-h", "--help"):
            print(msg)
            exit(0)
        elif opt_name in ("-i", "--input"):
            input_dir = opt_value
            inputs.append(input_dir)
        elif opt_name in ("-o", "--output"):
            output_dir = opt_value
            outputs.append(output_dir)
        elif opt_name in ("--ffmpeg",):
            ffmpeg = opt_value
    # check available
    input_len = len(inputs)
    output_len = len(outputs)
    if input_len == 0:
        panic("必须输入有input目录")

    if output_len == 0:
        for input_dir in inputs:
            input_output.append((input_dir, None))
    elif output_len == 1:
        for input_dir in inputs:
            input_output.append((input_dir, outputs[0]))
    elif input_len == output_len:
        input_output = zip(inputs, outputs)
    else:
        panic("output目录不唯一或无法与input完全匹配")

    if not ffmpeg:
        rs = os.popen("which ffmpeg")
        lines = rs.readlines()
        if len(lines) == 0:
            panic("未能找到ffmpeg, 请通过--ffmpeg指定ffmpeg文件位置")
        ffmpeg = lines[0].strip()
    return input_output, ffmpeg


class VideoExec:
    # 正在运行中的任务
    # running_tasks = 0

    def __init__(self, **kwargs):
        self.video = None
        self.audio = None
        self.title = None
        self.sub_title = None
        self.index = None
        self.input = None
        self.output = None
        self.ffmpeg = None

    def submit(self):
        output_dir = self.output + os.sep + self.title
        if not os.path.exists(output_dir):
            os.makedirs(self.output + os.sep + self.title)
        ffmpeg_cmd = '{ffmpeg} -threads 8 -i {video} -i {audio} -c:v copy -- "{output}".mp4'.format(
            ffmpeg=self.ffmpeg,
            video=self.video,
            audio=self.audio,
            output=output_dir + os.sep + str(self.index) + "-" + self.sub_title
        )
        os.system(ffmpeg_cmd)


def read_meta(input_dir):
    with open(input_dir + os.sep + "entry.json") as entry_file:
        entry_data = json.load(entry_file, encoding="utf-8")
        tag = entry_data['type_tag']
        video = VideoExec()
        video.index = entry_data['page_data']['page']
        video.audio = input_dir + os.sep + str(tag) + os.sep + "audio.m4s"
        video.video = input_dir + os.sep + str(tag) + os.sep + "video.m4s"
        video.title = entry_data['title'].encode('utf-8')
        video.sub_title = entry_data['page_data']['download_subtitle'].encode('utf-8')
        return video


def generate_meta(inputs_outputs, ffmpeg):
    for input_dir, output_dir in inputs_outputs:
        if not os.path.exists(input_dir):
            panic("input目录[{}]不存在, 请通过-h查看帮助重新输入".format(input_dir))
        if not output_dir:
            output_dir = input_dir + os.sep + "output-" + str(int(time.time()))
        for f_path, f_dirs, f_files in os.walk(input_dir):
            if "entry.json" in f_files:
                video_exec = read_meta(f_path)
                video_exec.input = input_dir
                video_exec.output = output_dir
                video_exec.ffmpeg = ffmpeg
                video_exec.submit()


if __name__ == '__main__':
    input_output_tuple, ffmpeg_path = process_args(sys.argv[1:])
    generate_meta(input_output_tuple, ffmpeg_path)
