import json
import os

from tasks import transcode, sleep, app
from subprocess import run, PIPE


SRC_RCLONE_PATH = "re-encode-raw-read:kikoeru-one/"
DST_RCLONE_PATH = "re-encode-m4a-upload:kikoeru-m4a/"

log = open("log.log", "a")


def write_log(msg):
    log.write(msg + "\n")
    log.flush()


def main():
    cmd = ["rclone", "ls", SRC_RCLONE_PATH, "--include", "*.wav", "--config", "rclone.conf", "--fast-list"]
    print(" ".join(cmd))
    res = run(cmd, stdout=PIPE)

    for file in res.stdout.decode().splitlines():
        file = " ".join(file.lstrip(" ").lstrip("\t").split(" ")[1:])

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
        're-encode-raw-read:kikoeru-one/導入部.wav',
        're-encode-m4a-upload:kikoeru-m4a/導入部.m4a'
    ).forget()


def test_2():
    sleep.delay(10)


def shutdown():
    app.control.shutdown()


if __name__ == '__main__':
    # test_2()
    # main()
    shutdown()
