import json
import os
import concurrent.futures
from typing import List

from tasks import transcode, sleep, app, update
from subprocess import run, PIPE

from utils.rclone import rclone_delete

SRC_RCLONE_PATH = "re-encode-raw-read:kikoeru-one/"
DST_RCLONE_PATH = "re-encode-m4a-v2-upload:kikoeru-m4a-v2/"

log = open("log.log", "a")


def write_log(msg):
    log.write(msg + "\n")
    log.flush()


def ls(path, include) -> List[str]:
    cmd = ["rclone", "ls", path, "--include", include, "--config", "rclone.conf", "--fast-list"]
    res = run(cmd, stdout=PIPE)

    files = res.stdout.decode().splitlines()

    # clean strings
    # "  6661590 kikoeru-m4a/available/そらまめ。/RJ140635 美味しいそらまめ採れました。/01 そらまめ売りの少女 導入部.m4a"
    # "kikoeru-m4a/available/そらまめ。/RJ140635 美味しいそらまめ採れました。/01 そらまめ売りの少女 導入部.m4a"
    files = list(map(
        lambda file: " ".join(file.lstrip(" ").lstrip("\t").split(" ")[1:]),
        files
    ))

    return files


def diff(
        pool,
        src=SRC_RCLONE_PATH,
        dst=DST_RCLONE_PATH,
        src_ext=".wav",
        dst_ext=".m4a"
) -> List[str]:
    print("list src files")
    src_files = pool.submit(ls, src, "*" + src_ext)  # ls(SRC_RCLONE_PATH, "*.wav")

    print("list dst files")
    dst_files = pool.submit(ls, dst, "*" + dst_ext)  # ls(DST_RCLONE_PATH, "*.m4a")

    src_files, dst_files = src_files.result(), dst_files.result()

    diff_files = list(
        set(src_files) -
        # 先把 dst 的文件后缀改成和 src 一样，再比较
        # 只比对文件名，不比对文件后缀
        set(list(map(lambda filename: filename[:-len(dst_ext)] + src_ext, dst_files)))
    )
    print("diff:", len(diff_files))
    return diff_files


def main():
    """
    增量转码 m4a, 不等待任务完成
    :return:
    """
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=32)

    futures = pool.map(
        lambda file:
        transcode.delay(
            os.path.join(SRC_RCLONE_PATH, file),
            os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a")
        ).forgot(),
        diff(pool)
    )

    pool.shutdown(wait=True)

    # for file in diff(pool):
    #     # skip if filename starts with ._
    #     if os.path.basename(file).startswith("."):
    #         continue
    #
    #     transcode.delay(
    #         os.path.join(SRC_RCLONE_PATH, file),
    #         os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a")
    #     ).forget()
    #
    #     write_log(
    #         json.dumps(
    #             [
    #                 os.path.join(SRC_RCLONE_PATH, file),
    #                 os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a")
    #             ]
    #         )
    #     )


def sync_main():
    """
    同步转码 m4a, 等待任务完成
    :return:
    """
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=32)

    futures = pool.map(
        lambda file:
        transcode.delay(
            os.path.join(SRC_RCLONE_PATH, file),
            os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a")
        ),
        diff(pool)
    )

    list(map(lambda future: future.get(), futures))


def test_error():
    transcode.delay(
        "example/error.wav",
        "example/error.m4a"
    ).get()


def test_normal():
    transcode.delay(
        "example/raw.wav",
        "example/raw.m4a"
    ).get()


def shutdown():
    app.control.shutdown()


def worker_update():
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=512)
    pool.map(lambda _: update.delay().get(), range(5000))
    pool.shutdown(wait=True)

    shutdown()


def delete_non_exist():
    """
    清理转码内容
    有时候原档因为更名、移动已经不存在了，m4a文件留着也没什么用
    就都清理掉
    :return:
    """
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=32)

    list(pool.map(
        lambda file:
        rclone_delete(os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a"), ["--config", "rclone.conf"]),
        diff(pool, DST_RCLONE_PATH, SRC_RCLONE_PATH, ".m4a", ".wav")
    ))

    pool.shutdown(wait=True)


if __name__ == '__main__':
    # 首次转码需要执行的
    # main()

    # 每日录入时需要执行的
    sync_main()
    delete_non_exist()

    # 升级需要执行的
    # worker_update()
    # shutdown()

    # 测试需要执行的
    # test_error()
    # test_normal()
