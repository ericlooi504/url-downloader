#!/usr/bin/env python3
"""
URL Directory Downloader
输入网页目录地址，下载该目录下的所有文件。
支持递归下载子目录、过滤扩展名、断点续传。
"""

import os
import sys
import re
import urllib.parse
import urllib.request
import argparse
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


class URLDirectoryDownloader:
    """网页目录文件下载器"""

    def __init__(self, base_url, output_dir="downloads",
                 recursive=False, extensions=None, threads=5,
                 delay=0, overwrite=False):
        self.base_url = base_url.rstrip("/")
        self.output_dir = Path(output_dir)
        self.recursive = recursive
        self.extensions = extensions          # e.g. [".pdf", ".jpg"]
        self.threads = threads
        self.delay = delay
        self.overwrite = overwrite
        self.downloaded = 0
        self.skipped = 0
        self.failed = 0

    def run(self):
        """主入口"""
        print(f"🔍 扫描: {self.base_url}")
        print(f"📂 保存到: {self.output_dir}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        files = self.scan_directory(self.base_url)
        if not files:
            print("❌ 未找到可下载的文件")
            return

        print(f"📄 发现 {len(files)} 个文件")
        self.download_files(files)
        self.print_summary()

    def scan_directory(self, url):
        """扫描网页目录，提取文件链接"""
        try:
            html = self._fetch_url(url)
        except Exception as e:
            print(f"  ⚠ 无法访问 {url}: {e}")
            return []

        files = []
        links = self._extract_links(html, url)

        for name, href in links:
            full_url = urllib.parse.urljoin(url, href)

            # 判断是文件还是目录
            if href.endswith("/") or href.rstrip("/") != href:
                # 可能是个子目录
                if self.recursive and not self._is_parent_ref(name):
                    print(f"  📁 进入子目录: {name}")
                    sub_files = self.scan_directory(full_url)
                    # 调整路径前缀
                    for f in sub_files:
                        f["rel_path"] = f"{name}/{f['rel_path']}"
                    files.extend(sub_files)
                continue

            # 过滤扩展名
            if self.extensions:
                ext = Path(name).suffix.lower()
                if ext not in self.extensions:
                    continue

            # 过滤上级引用
            if self._is_parent_ref(name):
                continue

            files.append({
                "url": full_url,
                "name": name,
                "rel_path": name,
            })

        return files

    def _fetch_url(self, url):
        """获取网页内容"""
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")

    def _extract_links(self, html, base_url):
        """从 HTML 中提取 href 链接"""
        links = []

        # 模式: Apache/Nginx 目录列表
        # <a href="file.pdf">file.pdf</a>
        for match in re.finditer(
            r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>',
            html, re.IGNORECASE
        ):
            href = match.group(1).strip()
            # 解析名字
            name_match = re.search(r'>([^<]+)</a>', match.group(0))
            name = name_match.group(1).strip() if name_match else href

            # 跳过查询参数、锚点、mailto
            if href.startswith("?") or href.startswith("#") or href.startswith("mailto:"):
                continue
            if href == "/" or href == "../":
                continue

            links.append((name, href))

        return links

    def _is_parent_ref(self, name):
        """检查是否为上级目录引用"""
        return name in ("../", "Parent Directory", "..", ".", "")

    def download_files(self, files):
        """多线程下载文件"""
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {
                executor.submit(self._download_file, f): f
                for f in files
            }
            for future in as_completed(futures):
                f = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"  ❌ {f['rel_path']}: {e}")
                    self.failed += 1

    def _download_file(self, file_info):
        """下载单个文件"""
        url = file_info["url"]
        rel_path = file_info["rel_path"]
        save_path = self.output_dir / rel_path

        if save_path.exists() and not self.overwrite:
            self.skipped += 1
            return

        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                content = resp.read()

            save_path.write_bytes(content)
            size_kb = len(content) / 1024
            print(f"  ✅ {rel_path} ({size_kb:.1f} KB)")
            self.downloaded += 1

            if self.delay > 0:
                time.sleep(self.delay)

        except Exception as e:
            raise RuntimeError(f"下载失败: {e}")

    def print_summary(self):
        """打印汇总"""
        total = self.downloaded + self.skipped + self.failed
        print(f"\n{'='*40}")
        print(f"📊 下载完成!")
        print(f"  ✅ 成功: {self.downloaded}")
        print(f"  ⏭  跳过: {self.skipped}")
        print(f"  ❌ 失败: {self.failed}")
        print(f"  📁 保存位置: {self.output_dir.resolve()}")
        print(f"{'='*40}")


def get_input(prompt, default=None):
    """交互式输入，带默认值"""
    if default:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    return input(f"{prompt}: ").strip()


def main():
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        parser = argparse.ArgumentParser(
            description="🌐 URL 目录文件下载器",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  %(prog)s https://example.com/files/
  %(prog)s https://example.com/files/ -o ./myfiles -r
  %(prog)s https://example.com/files/ -e .pdf .docx
  %(prog)s https://example.com/files/ -t 10 --delay 0.5
            """
        )
        parser.add_argument("url", help="网页目录地址")
        parser.add_argument("-o", "--output", default="downloads",
                            help="保存目录 (默认: downloads)")
        parser.add_argument("-r", "--recursive", action="store_true",
                            help="递归下载子目录")
        parser.add_argument("-e", "--extensions", nargs="+",
                            help="只下载指定扩展名，如 .pdf .jpg")
        parser.add_argument("-t", "--threads", type=int, default=5,
                            help="并发下载线程数 (默认: 5)")
        parser.add_argument("--delay", type=float, default=0,
                            help="每个文件下载后延迟秒数")
        parser.add_argument("--overwrite", action="store_true",
                            help="覆盖已存在的文件")
        args = parser.parse_args()
        url = args.url
        output = args.output
        recursive = args.recursive
        threads = args.threads
        delay = args.delay
        overwrite = args.overwrite
        ext_list = args.extensions
    else:
        # 交互式模式 — 引导用户输入
        print("=" * 40)
        print("  🌐 URL 目录文件下载器")
        print("=" * 40)
        print("直接回车使用默认值，输入 ? 查看帮助")
        print()
        url = get_input("请输入网页目录地址")
        if not url:
            print("❌ URL 不能为空")
            sys.exit(1)

        output = get_input("文件保存目录", "downloads")

        r = get_input("是否递归子目录 (y/n)", "n").lower()
        recursive = r in ("y", "yes")

        t = get_input("下载线程数", "5")
        threads = int(t) if t.isdigit() else 5

        e = get_input("仅下载指定扩展名 (留空下载全部，多个用空格分隔)", "")
        ext_list = e.split() if e else None

        overwrite_input = get_input("覆盖已存在的文件 (y/n)", "n").lower()
        overwrite = overwrite_input in ("y", "yes")

        delay = 0
        print()

    # 处理扩展名列表
    if ext_list:
        ext_list = [e.lower() if e.startswith(".") else f".{e.lower()}"
                    for e in ext_list]

    downloader = URLDirectoryDownloader(
        base_url=url,
        output_dir=output,
        recursive=recursive,
        extensions=ext_list,
        threads=threads,
        delay=delay,
        overwrite=overwrite,
    )

    try:
        downloader.run()
    except KeyboardInterrupt:
        print("\n⏹  用户中断")
    except Exception as e:
        print(f"\n💥 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
