# -*- coding: utf-8 -*-

import cv2
import numpy as np
import const
import utils
import measure
from kalman import Kalman
from ultralytics import YOLO
# --------------------------------Kalman参数---------------------------------------
# 状态转移矩阵，上一时刻的状态转移到当前时刻
A = np.array([[1, 0, 0, 0, 1, 0],
              [0, 1, 0, 0, 0, 1],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 1]])
# 控制输入矩阵B
B = None
# 过程噪声协方差矩阵Q，p(w)~N(0,Q)，噪声来自真实世界中的不确定性,
# 在跟踪任务当中，过程噪声来自于目标移动的不确定性（突然加速、减速、转弯等）
Q = np.eye(A.shape[0]) * 0.1
# 状态观测矩阵
H = np.array([[1, 0, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 0, 0]])
# 观测噪声协方差矩阵R，p(v)~N(0,R)
# 观测噪声来自于检测框丢失、重叠等
R = np.eye(H.shape[0]) * 1
# 状态估计协方差矩阵P初始化
P = np.eye(A.shape[0])
# -------------------------------------------------------------------------------


def main():

    cap = cv2.VideoCapture(const.VIDEO_PATH)

    yolo_model = YOLO('yolov8n.pt')


    sz = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
          int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video_writer = cv2.VideoWriter(const.VIDEO_OUTPUT_PATH, fourcc, const.FPS, sz, True)


    state_list = []
    frame_cnt = 1


    while cap.isOpened():

        ret, frame = cap.read()
        if not ret:
            break


        yolo_results = yolo_model(frame, conf=0.5, iou=0.4, classes=[0])
        meas_list_frame = []


        for result in yolo_results:
            boxes = result.boxes
            for box in boxes:

                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                meas_list_frame.append([x1, y1, x2, y2])

        for target in state_list:
            target.predict()


        mea_list = [utils.box2meas(mea) for mea in meas_list_frame]
        state_rem_list, mea_rem_list, match_list = Kalman.association(state_list, mea_list)


        state_del = []
        for idx in state_rem_list:
            status, _, _ = state_list[idx].update()
            if not status:
                state_del.append(idx)
        state_list = [state_list[i] for i in range(len(state_list)) if i not in state_del]


        for idx in mea_rem_list:
            new_state = Kalman(A, B, H, Q, R, utils.mea2state(mea_list[idx]), P)
            state_list.append(new_state)


        for mea in meas_list_frame:
            cv2.rectangle(frame, tuple(mea[:2]), tuple(mea[2:]), const.COLOR_MEA, thickness=1)


        for kalman in state_list:

            track_box = utils.state2box(kalman.X_posterior)
            cv2.rectangle(frame, tuple(track_box[:2]), tuple(track_box[2:]), const.COLOR_STA, thickness=2)
            track_points = kalman.track
            for p_idx in range(len(track_points) - 1):
                prev_pt = track_points[p_idx]
                curr_pt = track_points[p_idx + 1]
                cv2.line(frame, prev_pt, curr_pt, kalman.track_color, 2)
            future_points = kalman.predict_future_path(steps=5)
            if track_points:
                prev_pt = tuple(track_points[-1])
                for fut_pt in future_points:
                    cv2.line(frame, prev_pt, fut_pt, kalman.track_color, 1, lineType=cv2.LINE_AA)
                    cv2.circle(frame, fut_pt, 3, kalman.track_color, -1)
                    prev_pt = fut_pt
            pixel_speed = kalman.get_speed(const.FPS)
            meter_speed = pixel_speed * const.PIXEL_TO_METER
            speed_label = f"v={pixel_speed:.1f}px/s | {meter_speed:.2f}m/s"
            text_org = (track_box[0], max(track_box[1] - 10, 0))
            cv2.putText(frame, speed_label, text_org, cv2.FONT_HERSHEY_SIMPLEX, 0.5, kalman.track_color, 2)


        for match in match_list:
            det_pt = tuple(match[0][:2])
            track_pt = tuple(match[1][:2])
            cv2.line(frame, det_pt, track_pt, const.COLOR_MATCH, 3)


        cv2.putText(frame, str(frame_cnt), (0, 50),
                    color=const.RED, fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.5)


        cv2.imshow('YOLOv8 + Kalman 多目标跟踪', frame)
        cv2.imwrite(f"./image/{frame_cnt}.jpg", frame)
        video_writer.write(frame)

        # 控制帧显示速度
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break  # 按 q退出

        frame_cnt += 1

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
