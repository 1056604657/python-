#!/usr/bin/env python
# coding: utf-8


from langchain.retrievers import BM25Retriever
from langchain.schema import Document
from transformers import DataProcessor

from pdf_parse import DataProcess
import jieba

#words = line.split("\t")意思： 字符串 line 按制表符进行分割，并将分割后的子字符串存储在列表 words 中。例如，如果 line 的内容为 "apple\tbanana\torange", 那么执行这行代码后，words 的值将会是 ['apple', 'banana', 'orange']

#line = line.strip("\n").strip()意思 ，line.strip("\n")操作首先移除了字符串头尾的换行符（\n），然后继续使用strip()方法去除了头尾的空格和制表符（默认情况下）。在这样的处理过程中，主要是为了清除字符串两端不需要的空格、换行符等字符，以便对字符串进行后续操作，比如分割、比较或其他处理。因此，这行代码的作用是确保 line 字符串两端没有换行符和空格，并将处理后的结果重新赋值给 line 变量。

#tokens = " ".join(jieba.cut_for_search(line))意思， jieba.cut_for_search(line)函数会将输入的字符串line进行分词，返回一个生成器对象，里面包含了分词后的结果。然后" ".join()方法将这些分词结果用空格连接起来，形成一个字符串，存储在tokens变量中。

class BM25(object):

    def __init__(self, documents):

        docs = []
        full_docs = []                        
        for idx, line in enumerate(documents):  #起始第一次 idx=0, line='xxx
            if not isinstance(line, str):
                line = str(line)
            line = line.strip("\n").strip() 
            if(len(line)<5):
                continue
            tokens = " ".join(jieba.cut_for_search(line)) 
            docs.append(Document(page_content=tokens, metadata={"id": idx})) 
            words = line.split("\t") 
            full_docs.append(Document(page_content=words[0], metadata={"id": idx}))
        self.documents = docs
        self.full_documents = full_docs
        self.retriever = self._init_bm25()

    def _init_bm25(self):
        return BM25Retriever.from_documents(self.documents)

    def GetBM25TopK(self, query, topk):
        self.retriever.k = topk
        query = " ".join(jieba.cut_for_search(query))
        ans_docs = self.retriever.get_relevant_documents(query)
        ans = []
        for line in ans_docs:
            ans.append(self.full_documents[line.metadata["id"]])
        return ans
