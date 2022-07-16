import os

from tasks import transcode
from subprocess import run, PIPE


SRC_RCLONE_PATH = "local:./example"
DST_RCLONE_PATH = "local:./example_transcoded"


if __name__ == '__main__':
    res = run(["rclone", "ls", SRC_RCLONE_PATH, "--include", "*.wav", "--config", "rclone.conf"], stdout=PIPE)
    for file in res.stdout.decode().splitlines():
        file = file.split(" ")[-1]
        transcode.delay(
            os.path.join(SRC_RCLONE_PATH, file),
            os.path.join(DST_RCLONE_PATH, file[:-4] + ".m4a")
        ).forget()
