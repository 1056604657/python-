import hashlib
import os
from typing import Any, Dict, List, Union
from utils import *
import pdfplumber

class FileProcessor:
    # 定义允许处理的文件后缀列表，作为类属性
    ALLOWED_EXTENSIONS = ['.txt', '.pdf']

    def __init__(self, file_path):
        self.file_path = file_path

    # 获取文件后缀
    def get_file_extension(self):
        _, file_extension = os.path.splitext(self.file_path)
        return file_extension.lower()  # 转换为小写以方便比较

    def is_allowed_file(self):
        # 获取文件后缀
        file_extension = self.get_file_extension()

        # 检查文件后缀是否在允许处理的列表中
        return file_extension in self.ALLOWED_EXTENSIONS

    # 获取文件名（不包含后缀）
    def get_file_name(self):
        file_name = os.path.basename(self.file_path)
        return file_name

    # 获取文件MD5值
    # todo @staticmethod
    def get_file_md5(self):
        file_bytes = self.get_file_bytes(self.file_path)
        file_md5 = self.calculate_md5(file_bytes)
        return file_md5

    @staticmethod
    def get_file_bytes(file_path: str):
        # 打开文件
        with open(file_path, 'rb') as file:
            # 读取文件内容为字节流
            file_bytes = file.read()

        return file_bytes

    # 计算输入数据的MD5哈希值
    @staticmethod
    def calculate_md5(input_data: Union[str, bytes]) -> str:
        # 创建一个MD5对象
        md5 = hashlib.md5()

        # 判断输入是字符串还是字节流
        if isinstance(input_data, str):
            # 如果是字符串，将其编码为字节流再更新MD5对象的内容
            md5.update(input_data.encode('utf-8'))
        elif isinstance(input_data, bytes):
            # 如果已经是字节流，直接更新MD5对象的内容
            md5.update(input_data)
        else:
            raise ValueError("Input data must be either a string or bytes")
        return md5.hexdigest()  # 获取MD5哈希值，并以十六进制字符串的形式返回


if __name__ == "__main__":
    # 示例用法
    file_path = "assets\\sample-pdf.pdf"
    pdf = pdfplumber.open(file_path)
    # print(pdf.pages[0].extract_text())  ## 可复制的PDF
    pdf_content=[]
    for page_idx in range(len(pdf.pages)):
        pdf_content.append({
            "page": 'page_' + str(page_idx + 1),
            'content': pdf.pages[page_idx].extract_text()
        })
    print("pdf_content",pdf_content)
    processor = FileProcessor(file_path)
    result = processor.is_allowed_file()
    print(result)  # 输出 True 或 False
