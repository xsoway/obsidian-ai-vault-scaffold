#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2026/04/27 15:30
# @Filename : html-to-md.py
# @Author   : Alan_Hsu

"""
HTML 转 Markdown 一键脚本
支持本地文件和在线 URL 两种输入方式

用法:
    1. 本地文件:
        uv run python html-to-md.py /path/to/file.html

    2. 在线 URL:
        uv run python html-to-md.py "http://example.com/page.html"

依赖安装:
    uv pip install markdownify requests beautifulsoup4
"""

import argparse
import html
import logging
import os
import re
import sys
from urllib.parse import urlparse, unquote

import requests

try:
    from markdownify import markdownify as md
    HAS_MARKDOWNIFY = True
except ImportError:
    HAS_MARKDOWNIFY = False
    md = None

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    BeautifulSoup = None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def is_url(path: str) -> bool:
    """判断输入是否为 URL"""
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def download_html(url: str) -> str:
    """下载 HTML 内容"""
    logger.info(f"正在下载页面: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # 自动识别编码
        logger.info("页面下载成功")
        return response.text
    except requests.RequestException as e:
        logger.error(f"下载失败: {e}", exc_info=True)
        sys.exit(1)


def read_local_html(file_path: str) -> str:
    """读取本地 HTML 文件"""
    logger.info(f"正在读取文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文件失败: {e}", exc_info=True)
        sys.exit(1)


def extract_main_content(html_content: str) -> str:
    """尝试提取页面主要内容（可选，默认不启用）"""
    if not HAS_BS4:
        logger.warning("未安装 beautifulsoup4，跳过提取正文")
        return html_content
    soup = BeautifulSoup(html_content, 'html.parser')
    # 简单策略：优先找 article、main、body 标签
    main_elem = soup.find('article') or soup.find('main') or soup.body
    if main_elem:
        return str(main_elem)
    return html_content


def html_to_markdown(html_content: str, extract_body: bool = False) -> str:
    """HTML 转 Markdown"""
    logger.info("正在转换为 Markdown...")
    if extract_body:
        html_content = extract_main_content(html_content)
    # 使用 markdownify 转换，GFM 风格
    if HAS_MARKDOWNIFY:
        result = md(
            html_content,
            heading_style='ATX',
            bullets=['-', '+', '*'],
            code_language='text'
        )
        logger.info("转换完成")
        return result
    else:
        logger.warning("未安装 markdownify，返回原始 HTML")
        return html_content


def clean_markdown(text: str, keep_ui_noise: bool = False) -> str:
    """清洗 Markdown 冗余标签与内容"""
    logger.info("正在清洗冗余标签...")
    lines = text.splitlines()

    cleaned = []
    for line in lines:
        s = line.strip()

        # 删除整行 HTML 标签（如 <div ...>、</div>、<span ...>）
        if re.fullmatch(r'</?\w+[^>]*>', s):
            continue

        # 删除行内 HTML 标签
        line2 = re.sub(r'</?\w+[^>]*>', '', line)

        # HTML 实体解码
        line2 = html.unescape(line2)

        # 清理仅剩空白的行
        if line2.strip() == '':
            cleaned.append('')
        else:
            cleaned.append(line2.rstrip())

    # 压缩连续空行为最多 1 行
    final_lines = []
    blank = 0
    for l in cleaned:
        if l.strip() == '':
            blank += 1
            if blank <= 1:
                final_lines.append('')
        else:
            blank = 0
            final_lines.append(l)

    out = '\n'.join(final_lines).strip() + '\n'
    logger.info(f"清洗完成: {len(text)} -> {len(out)} 字符")
    return out


def generate_output_path(input_path: str) -> str:
    """根据输入路径生成输出路径"""
    if is_url(input_path):
        # 从 URL 提取文件名
        parsed = urlparse(input_path)
        path = unquote(parsed.path)
        filename = os.path.basename(path) or 'output'
        if not filename.endswith(('.html', '.htm')):
            filename += '.md'
        else:
            filename = os.path.splitext(filename)[0] + '.md'
    else:
        # 本地文件：换扩展名
        filename = os.path.splitext(os.path.basename(input_path))[0] + '.md'
    return filename


def main():
    parser = argparse.ArgumentParser(description='HTML 转 Markdown 一键工具')
    parser.add_argument('input', help='HTML 文件路径或 URL')
    parser.add_argument('-o', '--output', help='输出 Markdown 文件路径（可选）')
    parser.add_argument('--extract-body', action='store_true', help='尝试只提取页面主要内容（article/main）')
    parser.add_argument('--no-clean', action='store_true', help='不做冗余标签清洗')
    parser.add_argument('--keep-ui-noise', action='store_true', help='保留原型界面噪声文本（如状态栏、搜索框占位符等）')
    args = parser.parse_args()

    # 获取 HTML 内容
    if is_url(args.input):
        html_content = download_html(args.input)
    else:
        if not os.path.exists(args.input):
            logger.error(f"文件不存在: {args.input}")
            sys.exit(1)
        html_content = read_local_html(args.input)

    # 转换
    md_content = html_to_markdown(html_content, extract_body=args.extract_body)

    # 清洗
    if not args.no_clean:
        md_content = clean_markdown(md_content, keep_ui_noise=args.keep_ui_noise)

    # 确定输出路径
    output_path = args.output or generate_output_path(args.input)

    # 写入文件
    logger.info(f"正在写入: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        logger.info(f"成功！已生成: {output_path}")
    except Exception as e:
        logger.error(f"写入文件失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
