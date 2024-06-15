import os
from typing import List

import pdfplumber
import tiktoken

from config import CHUNK_OVERLAP, CHUNK_SIZE
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter     #使用到了langchain里面的文档分割方法


class FileProcessorHelper:
    def __init__(
            self,
            file_path: str,
            file_name: str = None,
            file_extension: str = None,
            file_md5: str = None,
    ):
        self.file_path = file_path
        self.file_name = file_name
        self.file_extension = file_extension
        self.file_md5 = file_md5

    # 获取docs
    def file_to_docs(self) -> List:

        strategy_mapping = {
            '.pdf': self.pdf_file_to_docs,
            '.txt': self.txt_file_to_docs,
            # '.doc': self.word_file_to_docs,
            # '.docx': self.word_file_to_docs,
            # '.md': self.md_file_to_docs,
            # '.xls': self.excel_file_to_docs,
            # '.xlsx': self.excel_file_to_docs,
            # '.csv': self.csv_file_to_docs,
            # '.jpg': self.image_file_to_docs,
            # '.jpeg': self.image_file_to_docs,
            # '.png': self.image_file_to_docs,
            # '.gif': self.image_file_to_docs,
            # '.ico': self.image_file_to_docs,
            # '.svg': self.image_file_to_docs,
            # '.bmp': self.image_file_to_docs,
            # '.ppt': self.ppt_file_to_docs,
            # '.pptx': self.ppt_file_to_docs,
            # '.zip': self.zip_file_to_docs,
            # '.mp3': self.audio_file_to_docs,
            # '.wav': self.audio_file_to_docs,
            # '.mp4': self.video_file_to_docs,
        }
        func = strategy_mapping.get(self.file_extension)  #<function FileProcessorHelper.pdf_file_to_docs at 0x0000000027D0CB80>
        return func(self.file_path)  #'assets\\sample-pdf.pdf'

    # 切分docs
    def split_docs(self, docs):
        # 切分
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,   #500
            chunk_overlap=CHUNK_OVERLAP, #100
            length_function=self.tiktoken_len,
        )
        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        docs = text_splitter.create_documents(texts, metadatas=metadatas)
        return docs

    @staticmethod
    def pdf_file_to_docs(file_path: str) -> List[Document]:   #file_path: 'assets\\sample-pdf.pdf'
        file_name = os.path.basename(file_path) #file_name:'sample-pdf.pdf'

        docs = []
        with pdfplumber.open(file_path) as pdf:  #pdf: <pdfplumber.pdf.PDF object at 0x0000000027D4D960>
            for page in pdf.pages:  #page: <Page:1>
                page_text = page.extract_text() #str格式（把pdf里面的文字内容，弄成了pdf格式）
                if page_text:
                    doc = Document(
                        page_content=page_text,
                        metadata=dict(
                            {
                                "file_name": file_name,
                                "page": page.page_number,  #int:1
                                "total_pages": len(pdf.pages), #int:1
                            },
                            **{
                                k: pdf.metadata[k]    #pdf.metadata类型{dict:5}也就是{'Author': 'Name', 'CreationDate': "D:20240508203945+08'00'", 'Creator': 'Microsoft® Word 适用于 Microsoft 365', 'ModDate': "D:20240508203945+08'00'", 'Producer': 'Microsoft® Word 适用于 Microsoft 365'}
                                for k in pdf.metadata
                                if isinstance(pdf.metadata[k], (str, int))
                            },
                        ),
                    )
                    docs.append(doc)
        return docs

    @staticmethod
    def txt_file_to_docs(file_path: str) -> List[Document]:
        file_name = os.path.basename(file_path)

        with open(file_path, 'r') as file:
            text = file.read()
        if not text:
            return []
        return [
            Document(
                page_content=text,
                metadata={
                    "file_name": file_name})]

    @staticmethod
    def tiktoken_len(text, model="gpt-3.5-turbo"):    #text为str类型 '你好\n你好有什么能帮你的吗？'
        """
        https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        :param text:
        :param model:
        :return:
        """
        # use cl100k_base tokenizer for gpt-3.5-turbo and gpt-4
        encoding = tiktoken.get_encoding('cl100k_base')  #<Encoding 'cl100k_base'>
        # encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(
            text,
            disallowed_special=()  # 禁用对所有特殊标记的检查
        )
        return len(tokens)  #int:17


if __name__ == "__main__":
    # 测试
    file_path = "assets\\sample-pdf.pdf"    #保证上传的是有效的PDF文件，保证里面有可复制的文字的内容，而不是纯图片格式
    file_name = "sample-pdf.pdf"
    file_extension = ".pdf"
    file_md5 = "e41ab92c3f938ddb3e82110becbbce3e"

    file_processor_helper = FileProcessorHelper(
        file_path=file_path,
        file_name=file_name,
        file_extension=file_extension,
        file_md5=file_md5,
    )
    docs = file_processor_helper.file_to_docs()
    print(docs)
    # 测试 tiktoken_len
    print(FileProcessorHelper.tiktoken_len("你好\n你好有什么能帮你的吗？"))