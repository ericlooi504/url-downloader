#!/usr/bin/env python3
"""
URL Directory Downloader — Kivy GUI 版本（用于打包 APK）
"""

import sys
import os
from pathlib import Path

# 导入核心下载器
from downloader import URLDirectoryDownloader

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform


class DownloaderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=15, spacing=10, **kwargs)

        # 标题
        title = Label(
            text="🌐 URL 目录下载器",
            size_hint_y=0.1,
            font_size="20sp",
            bold=True,
        )
        self.add_widget(title)

        # URL 输入
        url_box = BoxLayout(orientation="horizontal", size_hint_y=0.08)
        url_box.add_widget(Label(text="URL:", size_hint_x=0.15))
        self.url_input = TextInput(
            text="",
            hint_text="https://example.com/files/",
            multiline=False,
            size_hint_x=0.85,
        )
        url_box.add_widget(self.url_input)
        self.add_widget(url_box)

        # 输出目录 (含浏览按钮)
        out_box = BoxLayout(orientation="horizontal", size_hint_y=0.08)
        out_box.add_widget(Label(text="保存到:", size_hint_x=0.15))
        self.out_input = TextInput(
            text="downloads",
            multiline=False,
            size_hint_x=0.6,
        )
        out_box.add_widget(self.out_input)
        self.browse_btn = Button(text="📁 浏览", size_hint_x=0.25)
        self.browse_btn.bind(on_press=self.browse_folder)
        out_box.add_widget(self.browse_btn)
        self.add_widget(out_box)

        # 选项
        opts_box = BoxLayout(orientation="horizontal", size_hint_y=0.08)
        self.recursive_cb = CheckBox(active=False, size_hint_x=0.05)
        opts_box.add_widget(self.recursive_cb)
        opts_box.add_widget(Label(text="递归子目录", size_hint_x=0.2))
        opts_box.add_widget(Label(text="线程数:", size_hint_x=0.15))
        self.thread_spinner = Spinner(
            text="5",
            values=("1", "3", "5", "10", "20"),
            size_hint_x=0.15,
        )
        opts_box.add_widget(self.thread_spinner)
        opts_box.add_widget(Label(text="", size_hint_x=0.3))
        self.add_widget(opts_box)

        # 开始按钮
        self.start_btn = Button(
            text="🚀 开始下载",
            size_hint_y=0.1,
            background_color=(0.2, 0.6, 1, 1),
            font_size="18sp",
        )
        self.start_btn.bind(on_press=self.start_download)
        self.add_widget(self.start_btn)

        # 日志区域
        self.add_widget(Label(text="日志:", size_hint_y=0.05))
        scroll = ScrollView(size_hint_y=0.3)
        self.log_label = Label(
            text="就绪",
            size_hint_y=None,
            halign="left",
            valign="top",
            text_size=(Window.width - 40, None),
        )
        self.log_label.bind(texture_size=self.log_label.setter("size"))
        scroll.add_widget(self.log_label)
        self.add_widget(scroll)

        # 状态栏
        self.status_label = Label(
            text="等待操作...",
            size_hint_y=0.05,
            font_size="14sp",
        )
        self.add_widget(self.status_label)

    def browse_folder(self, _btn):
        """弹出文件夹选择器"""
        try:
            from tkinter import Tk, filedialog
            # Android 不支持 tkinter，跳过
            if platform == "android":
                self.status_label.text = "Android 上请手动输入路径"
                return
            root = Tk()
            root.withdraw()
            folder = filedialog.askdirectory(title="选择保存目录")
            root.destroy()
            if folder:
                self.out_input.text = folder
        except Exception as e:
            self.status_label.text = f"浏览失败: {e}"

    def log(self, msg):
        current = self.log_label.text
        self.log_label.text = f"{current}\n{msg}" if current != "就绪" else msg

    def start_download(self, _btn):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "⚠ 请输入 URL"
            return

        self.start_btn.disabled = True
        self.start_btn.text = "⏳ 下载中..."
        self.log_label.text = "就绪"
        self.status_label.text = f"扫描 {url} ..."

        output = self.out_input.text.strip() or "downloads"
        threads = int(self.thread_spinner.text)
        recursive = self.recursive_cb.active

        # 在后台线程运行
        from threading import Thread

        def run():
            try:
                dl = URLDirectoryDownloader(
                    base_url=url,
                    output_dir=output,
                    recursive=recursive,
                    threads=threads,
                )
                dl.run()
                Clock.schedule_once(lambda dt: self.on_complete(dl))
            except Exception as e:
                Clock.schedule_once(
                    lambda dt, err=e: self.on_error(str(err))
                )

        Thread(target=run, daemon=True).start()

    def on_complete(self, dl):
        self.start_btn.disabled = False
        self.start_btn.text = "🚀 开始下载"
        self.status_label.text = (
            f"✅ 完成: 成功 {dl.downloaded} / 跳过 {dl.skipped} / 失败 {dl.failed}"
        )
        self.log(f"\n{'='*30}")
        self.log(f"保存位置: {dl.output_dir.resolve()}")

    def on_error(self, err):
        self.start_btn.disabled = False
        self.start_btn.text = "🚀 开始下载"
        self.status_label.text = f"❌ 错误: {err[:60]}"


class DownloaderApp(App):
    def build(self):
        self.title = "URL 目录下载器"
        if platform != "android":
            Window.size = (480, 750)
        return DownloaderLayout()


if __name__ == "__main__":
    DownloaderApp().run()
