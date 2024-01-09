#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Project: txt_to_epub_and_mobi
# File   : main.py
import os
import re
import zipfile

from jinja2 import Environment, FileSystemLoader


def txt2epub(save_as_path, text_file_path, cover_image_path, bookname, author, step=1):
    """
    将文本文件转为epub格式
    :param save_as_path: 保存epub的文件路径
    :param text_file_path: 文本文件路径
    :param cover_image_path: 封面图片路径
    :param bookname: 书名
    :param author:作者
    :param step: 多少章节作文一个html文件
    :return:
    """
    print("输入文件为", text_file_path)
    if os.path.exists(text_file_path):
        print("开始转换文件")
        with open(text_file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # 英文章节
            # regex = "^\s*Chapter\s*[0123456789IVX]*"
            # 中文章节
            regex = r"^\s*([第卷][0123456789一二三四五六七八九十零〇百千两]*[章回部节集卷].*)\s*"
            # 分割成［'','章节1标题','章节1内容','章节2标题','章节2内容',......］
            splits = re.split(regex, content, flags=re.M)

            # 按章节分组[(章节1标题,章节1内容）,(章节2标题,章节2内容),...]
            items = [(splits[i], splits[i + 1]) for i in range(1, len(splits) - 1, 2)]
            items = [(item[0], item[1].replace("\u3000", "")) for item in items]
            items = [
                (item[0], item[1].replace("\n", "<br/>\u3000\u3000")) for item in items
            ]
            # 按step章节分组，组成　[[(章节标题,章节内容）,(章节标题,章节内容)],.....]
            # 后续写入压缩文件时，按分组作为一个xhtml文件
            parts = [items[i : i + step] for i in range(0, len(items), step)]

            if len(parts) > 0:
                # print("ok")
                tmploader = FileSystemLoader(os.path.abspath("./template/"))
                tmpenv = Environment(loader=tmploader)

                book = zipfile.ZipFile(save_as_path, "w")
                # images

                # container.xml
                book.write(
                    "./template/META-INF/container.xml", "META-INF/container.xml"
                )

                # text
                nav_tmp = tmpenv.get_template("text/nav.html")
                nav_html = nav_tmp.render(parts=parts, bookname=bookname)
                book.writestr("text/nav.html", nav_html)
                # print(nav_html)

                part_tmp = tmpenv.get_template("text/part.html")
                index = 0
                for part in parts:
                    index += 1
                    part_html = part_tmp.render(
                        part=part, part_index=index, bookname=bookname
                    )
                    # 此处文件名要和nav.html里保持一致。
                    book.writestr("text/part_%s.html" % index, part_html)

                # content.opf
                opf = tmpenv.get_template("content.opf")
                content_opf = opf.render(parts=parts, bookname=bookname, author=author)
                book.writestr("content.opf", content_opf)

                # cover.jpeg
                book.write("./template/cover.jpeg", "cover.jpeg")
                # mimetype
                book.write("./template/mimetype", "mimetype")
                # page_styles.css
                book.write("./template/page_styles.css", "page_styles.css")
                # stylesheet.css
                book.write("./template/stylesheet.css", "stylesheet.css")
                # titlepage.xhtml
                book.write("./template/titlepage.xhtml", "titlepage.xhtml")

                # toc.ncx
                ncx = tmpenv.get_template("toc.ncx")
                toc_ncx = ncx.render(parts=parts, bookname=bookname)
                book.writestr("toc.ncx", toc_ncx)
                # print(toc_ncx)

                book.close()

                print("转换完成.")
    else:
        print("源文件不存在")

    pass


input_txt = "input/戮仙.txt"
output_epub = "output/戮仙.epub"

# 判断文件是否存在
if os.path.exists(output_epub):
    # 删除文件
    os.remove(output_epub)
    print(f"文件 {output_epub} 已删除。")
else:
    print(f"文件 {output_epub} 不存在。")

txt2epub(output_epub, input_txt, "", bookname="戮仙", author="萧鼎")
