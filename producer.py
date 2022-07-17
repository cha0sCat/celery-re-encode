import json
import os
import concurrent.futures

from tasks import transcode, sleep, app
from subprocess import run, PIPE


SRC_RCLONE_PATH = "re-encode-raw-read:kikoeru-one/"
DST_RCLONE_PATH = "re-encode-m4a-upload:kikoeru-m4a/"

log = open("log.log", "a")


def write_log(msg):
    log.write(msg + "\n")
    log.flush()


def ls(path, include) -> list[str]:
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


def main():
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=32)

    print("list src files")
    src_files = pool.submit(ls, SRC_RCLONE_PATH, "*.wav")  # ls(SRC_RCLONE_PATH, "*.wav")

    print("list dst files")
    dst_files = pool.submit(ls, DST_RCLONE_PATH, "*.m4a")  # ls(DST_RCLONE_PATH, "*.m4a")

    src_files, dst_files = src_files.result(), dst_files.result()

    diff = list(
        set(src_files) -
        set(list(map(lambda filename: filename[:-4] + ".wav", dst_files)))
    )
    print("diff:", len(diff))

    for file in diff:
        # skip if filename starts with ._
        if os.path.basename(file).startswith("."):
            continue

        transcode.delay(
            os.path.join(SRC_RCLONE_PATH, file),
            os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a")
        ).forget()

        write_log(
            json.dumps(
                [
                    os.path.join(SRC_RCLONE_PATH, file),
                    os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a")
                ]
            )
        )


def test():
    transcode.delay(
        "example/error.wav",
        "example/error.m4a"
    ).get()


def shutdown():
    app.control.shutdown()


if __name__ == '__main__':
    main()
    # shutdown()
    # test()
