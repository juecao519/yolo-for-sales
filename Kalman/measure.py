# -*- coding: UTF-8 -*-

import re
import pathlib

import numpy as np
import cv2
import const


def load_measurement(file_dir):

    files = pathlib.Path(file_dir).rglob("testvideo1_*.txt")
    files = sorted(files, key=lambda x: int(re.findall("testvideo1_(.*?).txt", str(x))[0]))
    return [list(np.loadtxt(str(file), int, usecols=[1, 2, 3, 4])) for index, file in enumerate(files)]


if __name__ == "__main__":
    cap = cv2.VideoCapture(const.VIDEO_PATH)
    mea_list = load_measurement(const.FILE_DIR)

    for mea_frame_list in mea_list:
        ret, frame = cap.read()
        for mea in mea_frame_list:
            # print(mea)
            cv2.rectangle(frame, tuple(mea[:2]), tuple(mea[2:]), const.COLOR_MEA, thickness=1)

        cv2.imshow('Demo', frame)
        cv2.waitKey(100)  # 显示 1000 ms 即 1s 后消失

    cap.release()
    cv2.destroyAllWindows()
