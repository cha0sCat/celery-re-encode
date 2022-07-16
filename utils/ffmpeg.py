from subprocess import PIPE, run


class FFMpegError(Exception):
    pass


def ffmpeg_transcode(src: str, dst: str, extra_args: list = None):
    result = run(
        ["ffmpeg", "-i", src, dst] + (extra_args or []),
        stdout=PIPE, stderr=PIPE
    )

    if result.returncode != 0:
        raise FFMpegError(
            'ffmpeg transcode failed! \n'
            'src:{} dst:{} \n'
            'stdout:{} \n'
            'stderr:{}'.format(
                src,
                dst,
                result.stdout.decode(),
                result.stderr.decode()
            ))
