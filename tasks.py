import os
import time

from app import app
from celery import Task
from utils.rclone import rclone_copy, rclone_delete, RcloneDeleteError
from utils.ffmpeg import ffmpeg_transcode


EXTRA_ARGS = ["--config", "rclone.conf"]


@app.task(bind=True, soft_time_limit=16, time_limit=16, acks_late=True)
def sleep(self, seconds):
    time.sleep(seconds)


@app.task(bind=True)
def transcode(self: Task, src: str, dst: str):
    src_file_ext = os.path.splitext(src)[1]
    tmp_src_file_name = self.request.id + src_file_ext

    dst_file_ext = os.path.splitext(dst)[1]
    tmp_dst_file_name = self.request.id + dst_file_ext

    def cleanUp():
        try:
            rclone_delete(tmp_src_file_name, EXTRA_ARGS)
        except RcloneDeleteError:
            pass

        try:
            rclone_delete(tmp_dst_file_name, EXTRA_ARGS)
        except RcloneDeleteError:
            pass

    try:
        rclone_copy(src, tmp_src_file_name, EXTRA_ARGS)
        ffmpeg_transcode(tmp_src_file_name, tmp_dst_file_name)
        rclone_copy(tmp_dst_file_name, dst, EXTRA_ARGS)

        cleanUp()

    except Exception as e:
        cleanUp()
        self.retry(exc=e)
