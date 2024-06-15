import time
import traceback

from db_qdrant import *
from AssistantGPT import AssistantGPT
from file_processor import FileProcessor
from file_processor_helper import FileProcessorHelper
from bm25_retriever import *
from pdf_parse import *


def create_result_dict(code, msg=None, data=None):
    """s
    生成一个包含代码、消息和数据的字典，用于表示函数执行的结果。

    Parameters:
    - code (int): 表示执行结果的代码，通常用于指示成功或失败等状态。
    - msg (str, optional): 包含有关执行结果的描述性消息，可以为空。
    - data (any type, optional): 附加数据，可以是任何类型的对象。

    Returns:
    dict: 包含代码、消息和数据的字典对象。

    Example:
    >>> result = create_result_dict(200, "操作成功", {'user_id': 123, 'username': 'John'})
    >>> print(result)
    {'code': 200, 'msg': '操作成功', 'data': {'user_id': 123, 'username': 'John'}}
    """
    result = {
        'code': code,
        'msg': msg,
        'data': data
    }
    return result


def file_to_vectordb(file_path, file_name, file_extension, file_md5):

    collection_name = file_md5
    qdrant = Qdrant()

    points_count = qdrant.get_points_count(collection_name)

    if points_count == 0:
        # case 1: 刚创建完集合，集合里没有节点
        # 创建 FileProcessorHelper 类对象
        file_processor_helper = FileProcessorHelper(
            file_path=file_path,
            file_name=file_name,
            file_extension=file_extension,
            file_md5=file_md5,
        )

        docs = file_processor_helper.file_to_docs()
        #logger.trace(f"docs: {docs}")

        docs = file_processor_helper.split_docs(docs)
        texts = [doc.page_content for doc in docs]  #test为列表形式
        print("utils文件中file_to_vectordb函数里面texts内容：",texts) #['西瓜是葫芦科西瓜属一年生蔓生藤本植物，形态近似于球形或椭圆形，颜色有\n深绿、浅绿或带有黑绿条带或斑纹；瓜籽为黑色，呈椭圆形，头尖；茎枝粗壮，\n有淡黄褐色的柔毛；叶片如纸，呈三角状卵形，边缘呈波状。花果期 5—6 月。\n因9世纪自西域传入中国，因此得名西瓜。\n西瓜栽培历史：一种说法认为西瓜并非源于中国，而是产自于非洲，于西域传\n来，因此名为西瓜。另一种说法源于神农尝百草的传说，相传西瓜在神农尝百\n草时被发现，原名叫稀瓜，意思是水多肉稀的瓜，但后来传着传着就变成了西\n瓜。\n西瓜生长环境：西瓜喜温暖、干燥的气候、不耐寒，生长发育的最适温度 24-\n30 度，根系生长发育的最适温度 30-32 度，根毛发生的最低温度 14 度。西瓜\n在生长发育过程中需要较大的昼夜温差。', '30 度，根系生长发育的最适温度 30-32 度，根毛发生的最低温度 14 度。西瓜\n在生长发育过程中需要较大的昼夜温差。\n番茄：番茄（是茄科茄属的一年生草本植物，植株高达 2 米。转基因西红柿颜\n色鲜红，果实硬，不易裂果。番茄茎易倒伏；叶为羽状复叶，基部呈楔形，较\n偏斜，具有不规则的锯齿；花冠呈辐状，黄色，裂片为窄长圆形；浆果呈扁球\n形或近球形，肉质多汁液，为桔黄或鲜红色，表面光滑，花果期夏秋季；种子\n黄色，覆盖柔毛。\n番茄形态特征：番茄是茄科一年生草本植物，株高 0.6-2 米，全体生粘质腺毛，\n有强烈气味。茎易倒伏。叶羽状复叶或羽状深裂，长 10-40 厘米，小叶极不规\n则，大小不等，常 5-9 枚，卵形或矩圆形，长 5-7 厘米，边缘有不规则锯齿或\n裂片。']

        metadatas = [doc.metadata for doc in docs]

        # 向量化 docs
        payloads = build_payloads(texts, metadatas)
        gpt = AssistantGPT()
        embeddings = gpt.get_embeddings(texts)
        # 插入节点
        if qdrant.add_points(collection_name, embeddings, payloads):
            return file_path
    elif points_count > 0:
        # case 2: 库里已有该集合，且该集合有节点
        return file_path
    else:  # 等价于 points_count == -1
        # case 3: `创建集合失败`或`获取集合信息时发生错误`
        return ''


def upload_files(file_path):
    try:
        # 打印输入参数
        logger.info(f"输入参数 | file_path: {file_path} {type(file_path)}")

        # 检查输入参数
        if not file_path:
            return create_result_dict(400, '没有上传文件')

        # 创建 FileProcessor 类对象
        file_processor = FileProcessor(file_path=file_path)

        # 检查文件是否允许处理
        if not file_processor.is_allowed_file():
            # 文件后缀不允许处理，直接返回
            return create_result_dict(400, f'暂不支持此文件后缀: {file_path}')

        logger.trace(f"文件允许被处理 | file_path: {file_path}")

        # 处理文件
        # 获取文件的更多信息
        file_name = file_processor.get_file_name()
        file_extension = file_processor.get_file_extension()
        file_md5 = file_processor.get_file_md5()
        logger.info(
            f"文件信息 | file_name: {file_name}, file_extension: {file_extension}, file_md5: {file_md5}")

        # 文件存入向量数据库，返回一个路径而已
        uploaded_file_path = file_to_vectordb(
            file_path, file_name, file_extension, file_md5)

        # 处理成功
        if uploaded_file_path:
            # 处理成功
            return create_result_dict(
                200, None, {
                    'uploaded_file_path': uploaded_file_path
                })
        else:
            # 处理失败
            return create_result_dict(500)
    except Exception as e:
        # 打印完整错误信息
        error_str = traceback.format_exc()
        logger.error(error_str)
        # 处理失败
        return create_result_dict(500)


def build_context(qdrant, collection_names, question_vector, top_n):

    scored_points = []
    for collection_name in collection_names:
        scored_points_by_current_collection = qdrant.search(
            collection_name, question_vector, limit=top_n)
        scored_points.extend(scored_points_by_current_collection)

    # 将 ScoredPoint 对象列表转换为字典列表
    points = []
    for scored_point in scored_points:
        point = {
            "id": scored_point.id,
            "score": scored_point.score,
            "payload": scored_point.payload
        }
        points.append(point)

    # 字典列表按分数降序排序
    points.sort(key=lambda x: x['score'], reverse=True)
    points = points[:top_n]
    logger.trace(f"points: {points}")

    # 构建上下文
    contexts = []
    for point in points:
        context = point['payload']['page_content']
        contexts.append(context)
    context = "\n---\n".join(contexts)  #字符串类型

    return context

def build_chat_document_prompt(file_paths, user_input, chat_history, top_n):
    try:
        logger.debug(
            f"file_paths: {file_paths}, user_input: {user_input},  top_n: {top_n}")

        qdrant = Qdrant()

        collection_names = []
        if file_paths and any(file_paths):
            for file_path in file_paths:
                file_bytes = FileProcessor.get_file_bytes(file_path)
                file_md5 = FileProcessor.calculate_md5(file_bytes)
                collection_names.append(file_md5)
            logger.debug(f"上传文件的collection_names: {collection_names}")
        else:
            collection_names = qdrant.list_all_collection_names()
            logger.debug(f"未上传文件，Qdrant中已存在collection_names: {collection_names}")



        gpt = AssistantGPT()
        question_vectors = retry(gpt.get_embeddings, args=([user_input]))
        if not question_vectors:
            logger.error("获取 question_vector 参数失败")
            return ''
        question_vector = question_vectors[0]

        top_n = int(top_n)
        context = build_context(   
            qdrant,
            collection_names,
            question_vector,
            top_n)
        logger.trace(f"context: \n{context}")

        print("utils文件中build_chat_document_prompt函数里面file_pathsi内容：", file_paths) 
        data=[]
        for file_path in file_paths: #多文档上传后的解析示例['C:\\Users\\86156\\AppData\\Local\\Temp\\gradio\\65bb12cdbc11b7cf86dc3d7b5d23d44db89bb438\\sample-pdf.pdf', 'C:\\Users\\86156\\AppData\\Local\\Temp\\gradio\\a38be22e6d2eb1d3ce9e80b706cfdee9700bd7ec\\sample-pdf2.pdf']

            dp = DataProcess(pdf_path=file_path)  #pdf分块处理
            dp.ParseBlock(max_seq=1024)
            dp.ParseBlock(max_seq=512)
            dp.ParseAllPage(max_seq=256)
            dp.ParseAllPage(max_seq=512)
            dp.ParseOnePageWithRule(max_seq=256)
            dp.ParseOnePageWithRule(max_seq=512)
            # data = dp.data  # data为一整本的内容，列表类型data{list:8785}，很长很长
            # data.append(data)  #千万不要这样用，data 列表的内容附加到了自身，而不是将 dp.data 的内容附加到 data 列表中。导致循环引用，最终使得 data 中只有最后一个 dp.data 的内容。
            data.extend(dp.data)  #这一块很逻辑绕，多思考
        #print("utils文件中build_chat_document_prompt函数里面data内容：", data)  
        if data!=[]: 
            print("yes")
        else: print("NO")
        print("type(data)", type(data)) 
        #print("data",data) 
        bm25 = BM25(data)   
        res = bm25.GetBM25TopK(query=user_input, topk=5) 
        all_contents = [doc.page_content for doc in res]
        merged_content = '\n'.join(all_contents)
        context1 = context + "===============================\n" + merged_content 

        chat_history_str = ""
        for chat in chat_history[:-1]:  
            if chat[0]:
                chat_history_str += f'user:{chat[0]}\n'
            if chat[1]:
                chat_history_str += f'assistant:{chat[1]}\n'
        chat_history_str = chat_history_str[:-1] 
        logger.trace(f"chat_history_str: \n{chat_history_str}")

        prompt = f"""你是一个中文超低排放改造和评估专家，优先使用`文档内容`的内容来给出答案，如果不完整再结合你自己的知识补充。如果user的问题中没有提到哪个工厂，回复中就不要提到工厂名字（除非user要求），而是总结`文档内容`中的信息结合自己的知识回答。

文档内容：```
{context1}```

对话历史：```
{chat_history_str}```

user: ```{user_input}```
assistant: """
        logger.info(f"prompt: \n{prompt}")
        return prompt
    except Exception as e:
        error_str = traceback.format_exc()
        logger.error(error_str)
        return ''


def retry(func, args=None, kwargs=None, retries=3, delay=1):
    """
    重试机制函数
    :param func: 需要重试的函数
    :param args: 函数参数，以元组形式传入
    :param kwargs: 函数关键字参数，以字典形式传入
    :param retries: 重试次数，默认为3
    :param delay: 重试间隔时间，默认为1秒
    :return: 函数执行结果
    """
    for i in range(retries):
        try:
            if args is None and kwargs is None:
                result = func()
            elif args is not None and kwargs is None:
                result = func(*args)
            elif args is None and kwargs is not None:
                result = func(**kwargs)
            else:
                result = func(*args, **kwargs)
            return result  
        except Exception as e:
            logger.warning(f"{func.__name__}函数第{i + 1}次重试：{e}")
            time.sleep(delay)
    logger.error(f"{func.__name__}函数重试次数已用完")


def build_payloads(texts, metadatas):
    payloads = [
        {
            "page_content": text,
            "metadata": metadata,
        }
        for text, metadata in zip(texts, metadatas)
    ]
    return payloads
