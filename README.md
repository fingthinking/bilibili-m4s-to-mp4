# bilibili-m4s-to-mp4
B站m4s文件批量转mp4

```text
 python m4s_to_mp4.py -h                        

    描述: bilibili缓存m4s文件转mp4工具
    
    相关参数:
        -h, --help              展示当前说明
        -i, --input             [必须]视频合集所属文件夹或其父目录, 请务必包含entry.json文件
        -o, --output            [非必须]默认input同名目录下创建output-{timestamp}文件夹
        -p, --processor         [非必须]开启的进程数, 最多允许多少个进程同时执行转码    
            --ffmpeg            [非必须]ffmpeg文件所在位置, 非必须字段, 优先从which ffmpeg查找
```
