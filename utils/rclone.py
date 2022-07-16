from subprocess import PIPE, run


class RcloneCopyError(Exception):
    pass


class RcloneDeleteError(Exception):
    pass


def rclone_copy(src: str, dst: str, extra_args: list = None):
    result = run(
        ["rclone", "copyto", src, dst, "--b2-upload-cutoff", "100M"] + (extra_args or []),
        stdout=PIPE, stderr=PIPE
    )

    if result.returncode != 0:
        raise RcloneCopyError(
            'rclone copy failed! \n'
            'src:{} dst:{} \n'
            'stdout:{} \n'
            'stderr:{}'.format(
                src,
                dst,
                result.stdout.decode(),
                result.stderr.decode()
            ))


def rclone_delete(target: str, extra_args: list = None):
    result = run(
        ["rclone", "delete", target] + (extra_args or []),
        stdout=PIPE, stderr=PIPE
    )

    if result.returncode != 0:
        raise RcloneDeleteError(
            'rclone delete failed! \n'
            'target:{} \n'
            'stdout:{} \n'
            'stderr:{}'.format(
                target,
                result.stdout.decode(),
                result.stderr.decode()
            ))
