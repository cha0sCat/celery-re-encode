import os.path
from subprocess import PIPE, run

from utils.rclone import rclone_delete, RcloneDeleteError


class FFMpegError(Exception):
    pass


def single_channel_handler(src: str, dst: str, extra_args: list = None):
    result = run(
        ["ffmpeg", "-i", src, "-c:v", "copy", "-ac", "2", dst] + (extra_args or []),
        stdout=PIPE, stderr=PIPE
    )

    if result.returncode != 0:
        raise FFMpegError(
            'ffmpeg single_channel_handler failed! \n'
            'src:{} dst:{} \n'
            'stdout:{} \n'
            'stderr:{}'.format(
                src,
                dst,
                result.stdout.decode(errors='ignore'),
                result.stderr.decode(errors='ignore')
            ))


def input_contains_inf_handler(src: str, dst: str, extra_args: list = None):
    # Input contains (near) NaN/+-Infs/s
    run(["apt", "update"])
    run(["apt", "install", "sox", "libsox-fmt-mp3", "-y"])

    # fallback to sox

    # sox 原生不支持 m4a 需要先转换为 mp3，再转换为 m4a
    mid_file = os.path.splitext(dst)[0] + ".mp3"

    run(["sox", src, mid_file])
    result = run(["ffmpeg", "-i", mid_file, "-c:v", "copy", dst] + (extra_args or []))

    rclone_delete(mid_file, extra_args)

    if result.returncode != 0:
        raise FFMpegError(
            'sox input_contains_inf_handler failed! \n'
            'src:{} dst:{} \n'
            'stdout:{} \n'
            'stderr:{}'.format(
                src,
                dst,
                result.stdout.decode(errors='ignore'),
                result.stderr.decode(errors='ignore')
            ))


def ffmpeg_error_handler(exc: Exception, src: str, dst: str, extra_args: list = None):
    """
    尝试内部处理异常，处理不了再抛出错误
    """
    # delete dst file
    try:
        rclone_delete(dst, extra_args)
    except RcloneDeleteError:
        pass

    if "1 channels (FL)" in exc.args[0]:
        return single_channel_handler(src, dst, extra_args)

    elif "Input contains (near) NaN/+-Inf" in exc.args[0]:
        return input_contains_inf_handler(src, dst, extra_args)

    else:
        raise exc


def ffmpeg_transcode(src: str, dst: str, extra_args: list = None):
    result = run(
        ["ffmpeg", "-i", src, "-c:v", "copy", dst] + (extra_args or []),
        stdout=PIPE, stderr=PIPE
    )

    if result.returncode != 0:
        exc = FFMpegError(
            'ffmpeg transcode failed! \n'
            'src:{} dst:{} \n'
            'stdout:{} \n'
            'stderr:{}'.format(
                src,
                dst,
                result.stdout.decode(errors='ignore'),
                result.stderr.decode(errors='ignore')
            ))

        return ffmpeg_error_handler(
            exc,
            src,
            dst,
            extra_args
        )
