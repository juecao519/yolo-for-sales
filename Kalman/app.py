# -*- coding: utf-8 -*-

import cv2
import numpy as np
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
import threading
import const
import utils
import measure
from kalman import Kalman
from ultralytics import YOLO

kivy.require('2.1.0')

# Kalman参数
A = np.array([[1, 0, 0, 0, 1, 0],
              [0, 1, 0, 0, 0, 1],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 1]])
B = None
Q = np.eye(A.shape[0]) * 0.1
H = np.array([[1, 0, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0],
              [0, 0, 1, 0, 0, 0],
              [0, 0, 0, 1, 0, 0]])
R = np.eye(H.shape[0]) * 1
P = np.eye(A.shape[0])


class SpeedCalculator:
    """速度计算器"""
    def __init__(self, reference_distance_m=10.0, fps=30):
        """
        :param reference_distance_m: 参考距离（米），用于标定像素到实际距离的转换
        :param fps: 视频帧率
        """
        self.reference_distance_m = reference_distance_m
        self.fps = fps
        self.pixels_per_meter = None  # 需要标定
        self.track_history = {}  # 存储每个目标的轨迹历史 {track_id: [(x, y, frame_num), ...]}
        
    def calibrate(self, pixel_distance, real_distance_m):
        """标定：根据已知的像素距离和实际距离计算转换系数"""
        if pixel_distance > 0:
            self.pixels_per_meter = pixel_distance / real_distance_m
            return True
        return False
    
    def calculate_speed(self, track_id, current_pos, frame_num):
        """计算速度（km/h）"""
        if track_id not in self.track_history:
            self.track_history[track_id] = []
        
        self.track_history[track_id].append((current_pos[0], current_pos[1], frame_num))
        
        # 只保留最近2秒的轨迹
        max_frames = self.fps * 2
        if len(self.track_history[track_id]) > max_frames:
            self.track_history[track_id] = self.track_history[track_id][-max_frames:]
        
        if len(self.track_history[track_id]) < 2:
            return 0.0
        
        if self.pixels_per_meter is None:
            return 0.0
        
        # 计算最近几帧的平均速度
        history = self.track_history[track_id]
        if len(history) < 5:
            return 0.0
        
        # 使用最近5帧计算速度
        recent = history[-5:]
        total_pixel_distance = 0
        total_frames = 0
        
        for i in range(1, len(recent)):
            dx = recent[i][0] - recent[i-1][0]
            dy = recent[i][1] - recent[i-1][1]
            pixel_distance = np.sqrt(dx*dx + dy*dy)
            total_pixel_distance += pixel_distance
            total_frames += 1
        
        if total_frames == 0:
            return 0.0
        
        avg_pixel_distance_per_frame = total_pixel_distance / total_frames
        # 转换为米/秒
        meters_per_second = (avg_pixel_distance_per_frame * self.fps) / self.pixels_per_meter
        # 转换为公里/小时
        km_per_hour = meters_per_second * 3.6
        
        return km_per_hour
    
    def clear_track(self, track_id):
        """清除某个轨迹的历史"""
        if track_id in self.track_history:
            del self.track_history[track_id]


class VehicleSpeedApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cap = None
        self.yolo_model = None
        self.state_list = []
        self.frame_cnt = 0
        self.is_running = False
        self.speed_calculator = SpeedCalculator(fps=30)
        self.track_id_map = {}  # 映射Kalman对象到track_id
        self.next_track_id = 0
        
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title = Label(text='Vehicle Speed Monitor', size_hint_y=None, height=50, 
                     font_size=24, bold=True)
        main_layout.add_widget(title)
        
        # 图像显示区域
        self.image_widget = Image(size_hint_y=0.7)
        main_layout.add_widget(self.image_widget)
        
        # 信息显示区域
        info_layout = BoxLayout(orientation='vertical', size_hint_y=0.15, spacing=5)
        self.info_label = Label(text='Ready', size_hint_y=0.5, font_size=16)
        self.speed_label = Label(text='Speed: -- km/h', size_hint_y=0.5, font_size=18, 
                                color=(1, 0, 0, 1), bold=True)
        info_layout.add_widget(self.info_label)
        info_layout.add_widget(self.speed_label)
        main_layout.add_widget(info_layout)
        
        # 控制按钮区域
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10)
        
        self.start_button = Button(text='Start', on_press=self.start_detection)
        self.stop_button = Button(text='Stop', on_press=self.stop_detection, disabled=True)
        self.calibrate_button = Button(text='Calibrate', on_press=self.show_calibrate_popup)
        self.settings_button = Button(text='Settings', on_press=self.show_settings_popup)
        
        button_layout.add_widget(self.start_button)
        button_layout.add_widget(self.stop_button)
        button_layout.add_widget(self.calibrate_button)
        button_layout.add_widget(self.settings_button)
        
        main_layout.add_widget(button_layout)
        
        return main_layout
    
    def on_start(self):
        """应用启动时初始化"""
        try:
            # 初始化YOLO模型
            self.info_label.text = 'Loading model...'
            # 加载模型，如果本地没有会自动下载
            self.yolo_model = YOLO('yolov8n.pt')
            self.info_label.text = 'Model ready. Tap Start to begin'
        except Exception as e:
            self.info_label.text = f'Failed to load model: {str(e)}'
    
    def start_detection(self, instance):
        """开始检测"""
        try:
            # 打开摄像头（0为默认摄像头，Android上可能需要不同的索引）
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                # 尝试其他摄像头索引
                for i in range(1, 5):
                    self.cap = cv2.VideoCapture(i)
                    if self.cap.isOpened():
                        break
                
                if not self.cap.isOpened():
                    self.info_label.text = 'Cannot open camera'
                    return
            
            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.is_running = True
            self.state_list = []
            self.frame_cnt = 0
            self.track_id_map = {}
            self.next_track_id = 0
            
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.info_label.text = 'Detecting...'
            
            # 启动更新循环
            Clock.schedule_interval(self.update_frame, 1.0/30.0)  # 30 FPS
            
        except Exception as e:
            self.info_label.text = f'Failed to start: {str(e)}'
    
    def stop_detection(self, instance):
        """停止检测"""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.info_label.text = 'Stopped'
        self.speed_label.text = 'Speed: -- km/h'
        
        # 取消定时器
        Clock.unschedule(self.update_frame)
    
    def update_frame(self, dt):
        """更新帧"""
        if not self.is_running or not self.cap:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            self.info_label.text = 'Cannot read camera feed'
            return
        
        # 水平翻转（镜像效果，更符合用户习惯）
        frame = cv2.flip(frame, 1)
        
        # YOLO检测
        if self.yolo_model:
            # YOLO类别: 2=car, 3=motorcycle, 5=bus, 7=truck
            yolo_results = self.yolo_model(frame, conf=0.5, iou=0.4, classes=[2, 3, 5, 7])  # 车辆类别
            meas_list_frame = []
            
            for result in yolo_results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                    meas_list_frame.append([x1, y1, x2, y2])
        
        # Kalman预测
        for target in self.state_list:
            target.predict()
        
        # 数据关联
        mea_list = [utils.box2meas(mea) for mea in meas_list_frame]
        state_rem_list, mea_rem_list, match_list = Kalman.association(self.state_list, mea_list)
        
        # 更新已匹配的状态
        state_del = []
        for idx in state_rem_list:
            status, _, _ = self.state_list[idx].update()
            if not status:
                state_del.append(idx)
        self.state_list = [self.state_list[i] for i in range(len(self.state_list)) if i not in state_del]
        
        # 为未匹配的检测创建新轨迹
        for idx in mea_rem_list:
            new_state = Kalman(A, B, H, Q, R, utils.mea2state(mea_list[idx]), P)
            self.state_list.append(new_state)
            # 分配track_id
            self.track_id_map[id(new_state)] = self.next_track_id
            self.next_track_id += 1
        
        # 绘制检测框
        for mea in meas_list_frame:
            cv2.rectangle(frame, tuple(mea[:2]), tuple(mea[2:]), const.COLOR_MEA, thickness=2)
        
        # 绘制跟踪框和轨迹，并计算速度
        max_speed = 0.0
        speed_texts = []
        
        for kalman in self.state_list:
            track_box = utils.state2box(kalman.X_posterior)
            cv2.rectangle(frame, tuple(track_box[:2]), tuple(track_box[2:]), const.COLOR_STA, thickness=2)
            
            # 绘制轨迹
            track_points = kalman.track
            for p_idx in range(len(track_points) - 1):
                prev_pt = tuple(track_points[p_idx])
                curr_pt = tuple(track_points[p_idx + 1])
                cv2.line(frame, prev_pt, curr_pt, kalman.track_color, 2)
            
            # 计算速度
            track_id = self.track_id_map.get(id(kalman), -1)
            if track_id >= 0 and len(track_points) > 0:
                current_pos = track_points[-1]
                speed = self.speed_calculator.calculate_speed(track_id, current_pos, self.frame_cnt)
                
                if speed > max_speed:
                    max_speed = speed
                
                # 在框上方显示速度
                if speed > 0:
                    speed_text = f'{speed:.1f} km/h'
                    speed_texts.append((track_box, speed_text))
                    cv2.putText(frame, speed_text, (track_box[0], track_box[1] - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # 更新速度显示
        if max_speed > 0:
            self.speed_label.text = f'Top speed: {max_speed:.1f} km/h'
        else:
            self.speed_label.text = 'Speed: -- km/h'
        
        # 绘制匹配线
        for match in match_list:
            det_pt = tuple(match[0][:2])
            track_pt = tuple(match[1][:2])
            cv2.line(frame, det_pt, track_pt, const.COLOR_MATCH, 2)
        
        # 显示帧数
        cv2.putText(frame, f'Frame: {self.frame_cnt}', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 转换为Kivy纹理并显示
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.flip(frame_rgb, 0)  # 垂直翻转以适配Kivy
        
        buf = frame_rgb.tobytes()
        texture = Texture.create(size=(frame_rgb.shape[1], frame_rgb.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        self.image_widget.texture = texture
        
        self.frame_cnt += 1
    
    def show_calibrate_popup(self, instance):
        """显示标定弹窗"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        info_label = Label(text='Calibration:\nEnter real-world distance (m)\nand corresponding pixel distance',
                          size_hint_y=0.3, text_size=(None, None))
        content.add_widget(info_label)
        
        distance_input = TextInput(hint_text='Real distance (m)', multiline=False, size_hint_y=0.2)
        pixel_input = TextInput(hint_text='Pixel distance', multiline=False, size_hint_y=0.2)
        
        content.add_widget(distance_input)
        content.add_widget(pixel_input)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
        
        def calibrate(btn):
            try:
                distance = float(distance_input.text)
                pixels = float(pixel_input.text)
                if self.speed_calculator.calibrate(pixels, distance):
                    popup.dismiss()
                    self.info_label.text = f'Calibrated: {pixels:.0f}px = {distance:.1f}m'
                else:
                    self.info_label.text = 'Calibration failed: invalid numbers'
            except ValueError:
                self.info_label.text = 'Calibration failed: enter numbers'
        
        ok_button = Button(text='OK', on_press=calibrate)
        cancel_button = Button(text='Cancel', on_press=lambda x: popup.dismiss())
        
        button_layout.add_widget(ok_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)
        
        popup = Popup(title='Speed Calibration', content=content, size_hint=(0.8, 0.6))
        popup.open()
    
    def show_settings_popup(self, instance):
        """显示设置弹窗"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        info_label = Label(text='Settings', size_hint_y=0.2)
        content.add_widget(info_label)
        
        fps_input = TextInput(hint_text=f'FPS (current: {self.speed_calculator.fps})', 
                             multiline=False, size_hint_y=0.2)
        content.add_widget(fps_input)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.2)
        
        def save_settings(btn):
            try:
                if fps_input.text:
                    fps = int(fps_input.text)
                    if fps > 0:
                        self.speed_calculator.fps = fps
                        self.info_label.text = f'FPS set to {fps}'
                popup.dismiss()
            except ValueError:
                self.info_label.text = 'Enter a valid FPS'
        
        ok_button = Button(text='Save', on_press=save_settings)
        cancel_button = Button(text='Cancel', on_press=lambda x: popup.dismiss())
        
        button_layout.add_widget(ok_button)
        button_layout.add_widget(cancel_button)
        content.add_widget(button_layout)
        
        popup = Popup(title='Settings', content=content, size_hint=(0.8, 0.5))
        popup.open()
    
    def on_stop(self):
        """应用关闭时清理资源"""
        self.stop_detection(None)


if __name__ == '__main__':
    VehicleSpeedApp().run()

