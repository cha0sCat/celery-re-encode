import os

from tasks import transcode, sleep
from subprocess import run, PIPE


SRC_RCLONE_PATH = "re-encode-raw-read:kikoeru-one/"
DST_RCLONE_PATH = "re-encode-m4a-upload:kikoeru-m4a/"


def main():
    cmd = ["rclone", "ls", SRC_RCLONE_PATH, "--include", "*.wav", "--config", "rclone.conf", "--fast-list"]
    print(" ".join(cmd))
    res = run(["rclone", "ls", SRC_RCLONE_PATH, "--include", "*.wav", "--config", "rclone.conf"], stdout=PIPE)
    for file in res.stdout.decode().splitlines():
        file = " ".join(file.lstrip(" ").lstrip("\t").split(" ")[1:])
        transcode.delay(
            os.path.join(SRC_RCLONE_PATH, file),
            os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a")
        ).forget()
        break


def test():
    transcode.delay(
        're-encode-raw-read:kikoeru-one/導入部.wav',
        're-encode-m4a-upload:kikoeru-m4a/導入部.m4a'
    ).forget()


def test_2():
    sleep.delay(15)


if __name__ == '__main__':
    test_2()
