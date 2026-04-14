[app]

# (str) 应用标题
title = 车辆速度检测

# (str) 包名
package.name = vehiclespeed

# (str) 包域名
package.domain = org.example

# (str) 源代码目录
source.dir = .

# (list) 应用源代码
# 如果需要包含其他文件，使用逗号分隔
source.include_exts = py,png,jpg,jpeg,atlas,json,txt,pt

# (list) 应用排除的文件
# source.exclude_exts = spec

# (list) 应用排除的目录
source.exclude_dirs = tests, bin, venv, __pycache__, data

# (str) 应用版本
version = 0.1

# (list) 应用要求
# 在requirements.txt中列出的依赖会自动包含
requirements = python3,kivy,opencv-python,numpy,networkx,ultralytics,pillow,pyjnius,android

# (str) 自定义源码树，默认为local
# source.include_exts = py,png,jpg,kv,atlas

# (str) 应用图标
# icon.filename = %(source.dir)s/icon.png

# (str) 应用图标和启动画面
# 如果未指定，将使用默认的Kivy图标
# presplash.filename = %(source.dir)s/presplash.png

# (str) 应用图标（Android）
# icon.filename = %(source.dir)s/icon.png

# (str) 启动画面（Android）
# presplash.filename = %(source.dir)s/presplash.png

# (str) 应用图标（iOS）
# icon.filename = %(source.dir)s/icon.png

# (str) 启动画面（iOS）
# presplash.filename = %(source.dir)s/presplash.png

# (str) 应用图标（Windows）
# icon.filename = %(source.dir)s/icon.png

# (str) 启动画面（Windows）
# presplash.filename = %(source.dir)s/presplash.png

# (str) 应用图标（macOS）
# icon.filename = %(source.dir)s/icon.png

# (str) 启动画面（macOS）
# presplash.filename = %(source.dir)s/presplash.png

# (str) 应用图标（Linux）
# icon.filename = %(source.dir)s/icon.png

# (str) 启动画面（Linux）
# presplash.filename = %(source.dir)s/presplash.png

# (list) 应用权限（Android）
android.permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Android API级别
android.api = 30

# (int) 最小Android API级别
android.minapi = 21

# (str) Android NDK版本
android.ndk = 23b

# (int) Android SDK版本
android.sdk = 30

# (str) Android架构
android.archs = arm64-v8a, armeabi-v7a

# (bool) 启用AndroidX支持
android.enable_androidx = True

# (str) 应用入口点
# 如果使用app.py作为主文件，则不需要修改
# main.py = %(source.dir)s/main.py

# (str) 完整的应用类名
# 如果使用app.py，则不需要修改
# fullscreen = 1

# (str) 应用方向（Android）
# orientation = portrait

# (list) 应用包含的额外文件
# include.files = 

# (list) 应用排除的文件
# exclude.files = 

# (str) Python版本
# python.version = 3

# (bool) 如果为True，则跳过Python的安装步骤
# skip_python_install = False

# (list) 应用包含的额外Python模块
# include.modules = 

# (list) 应用排除的Python模块
# exclude.modules = 

# (str) 日志级别
# log_level = 2

# (bool) 如果为True，则显示构建过程中的详细输出
# verbose = True

# (bool) 如果为True，则显示构建过程中的警告
# warn_on_root = True

# (str) Android应用ID
# android.app_id = 

# (str) Android应用名称
# android.app_name = 

# (str) Android应用版本代码
# android.version_code = 1

# (str) Android应用版本名称
# android.version_name = 1.0

# (str) Android应用图标
# android.icon = 

# (str) Android应用启动画面
# android.presplash = 

# (str) Android应用主题
# android.theme = 

# (list) Android应用包含的额外文件
# android.include_files = 

# (list) Android应用排除的文件
# android.exclude_files = 

# (str) Android应用包类型
# android.package_type = apk

# (bool) 如果为True，则启用Android调试
# android.debug = True

# (str) Android密钥库路径
# android.keystore = 

# (str) Android密钥库密码
# android.keystore_password = 

# (str) Android密钥别名
# android.keyalias = 

# (str) Android密钥密码
# android.keyalias_password = 

# (list) Android应用包含的额外库
# android.add_jars = 

# (list) Android应用包含的额外Java文件
# android.add_src = 

# (list) Android应用包含的额外AAR文件
# android.add_aars = 

# (list) Android应用包含的额外资源
# android.add_resources = 

# (list) Android应用包含的额外资产
# android.add_assets = 

# (list) Android应用包含的额外清单文件
# android.add_manifest_xml = 

# (list) Android应用包含的额外权限
# android.add_permissions = 

# (list) Android应用包含的额外活动
# android.add_activities = 

# (list) Android应用包含的额外服务
# android.add_services = 

# (list) Android应用包含的额外接收器
# android.add_receivers = 

# (list) Android应用包含的额外提供者
# android.add_providers = 

# (str) iOS应用ID
# ios.app_id = 

# (str) iOS应用名称
# ios.app_name = 

# (str) iOS应用版本代码
# ios.version_code = 1

# (str) iOS应用版本名称
# ios.version_name = 1.0

# (str) iOS应用图标
# ios.icon = 

# (str) iOS应用启动画面
# ios.presplash = 

# (list) iOS应用包含的额外文件
# ios.include_files = 

# (list) iOS应用排除的文件
# ios.exclude_files = 

# (str) iOS应用包类型
# ios.package_type = ipa

# (bool) 如果为True，则启用iOS调试
# ios.debug = True

# (str) iOS开发团队ID
# ios.development_team = 

# (str) iOS配置文件
# ios.provisioning_profile = 

# (str) iOS证书
# ios.certificate = 

# (str) iOS证书密码
# ios.certificate_password = 

# (list) iOS应用包含的额外框架
# ios.add_frameworks = 

# (list) iOS应用包含的额外库
# ios.add_libs = 

# (list) iOS应用包含的额外资源
# ios.add_resources = 

# (list) iOS应用包含的额外资产
# ios.add_assets = 

# (list) iOS应用包含的额外权限
# ios.add_permissions = 

# (str) Windows应用ID
# windows.app_id = 

# (str) Windows应用名称
# windows.app_name = 

# (str) Windows应用版本代码
# windows.version_code = 1

# (str) Windows应用版本名称
# windows.version_name = 1.0

# (str) Windows应用图标
# windows.icon = 

# (str) Windows应用启动画面
# windows.presplash = 

# (list) Windows应用包含的额外文件
# windows.include_files = 

# (list) Windows应用排除的文件
# windows.exclude_files = 

# (str) Windows应用包类型
# windows.package_type = exe

# (bool) 如果为True，则启用Windows调试
# windows.debug = True

# (str) macOS应用ID
# macos.app_id = 

# (str) macOS应用名称
# macos.app_name = 

# (str) macOS应用版本代码
# macos.version_code = 1

# (str) macOS应用版本名称
# macos.version_name = 1.0

# (str) macOS应用图标
# macos.icon = 

# (str) macOS应用启动画面
# macos.presplash = 

# (list) macOS应用包含的额外文件
# macos.include_files = 

# (list) macOS应用排除的文件
# macos.exclude_files = 

# (str) macOS应用包类型
# macos.package_type = app

# (bool) 如果为True，则启用macOS调试
# macos.debug = True

# (str) Linux应用ID
# linux.app_id = 

# (str) Linux应用名称
# linux.app_name = 

# (str) Linux应用版本代码
# linux.version_code = 1

# (str) Linux应用版本名称
# linux.version_name = 1.0

# (str) Linux应用图标
# linux.icon = 

# (str) Linux应用启动画面
# linux.presplash = 

# (list) Linux应用包含的额外文件
# linux.include_files = 

# (list) Linux应用排除的文件
# linux.exclude_files = 

# (str) Linux应用包类型
# linux.package_type = AppImage

# (bool) 如果为True，则启用Linux调试
# linux.debug = True


