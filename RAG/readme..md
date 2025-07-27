>
What is the name of the ship owner's daughter?
What happend to boat
who is the child of the ship owner?
who is the child of the boatman?
what did john do when he was 23?
船主的女儿的名字是什么?
who is pandora
is pandora married
does pandora has sister or brothers
how old is pandora

> open-webui serve
> pipreqs . --force

## langchain_01_paraphrase_Chroma_gemini
- embedding_model_name:sbert(paraphrase-multilingual-mpnet-base-v2)
- vector db:Chroma(local)
- llm:gemini
- tried to use pca convert 768d to 128d
- score the context of retriever

## langchain_02_nomic_qdrant_gemini
### qdrant identify data by id,not by metadata,so metadata={"id": common_util.gen_md5(texts[i])} does not work,should set Document(page_content=texts[i], id=common_util.gen_md5(texts[i]))
        for i in range(len(texts))
- embedding_model_name:nomic-ai/nomic-embed-text-v1 or nomic-embed-text
- vector db:Qdrant(cloud)
- llm:gemini
- score the context of retriever
## langchain_03_nomic_Chroma_llama3.2
## langchain_04_nomic_Chroma_gemini_with_memory

### 网页
- crawl4ai <font color="red">ok</font>
- firecrawl <font color="orange">pass</font>
- scrapegraph ai <font color="orange">pass</font>
### 文档
- docling <font color="red">ok</font>
- lama parse <font color="orange">pass</font>
- megaparser <font color="orange">pass</font>
- extractthinker <font color="orange">pass</font>
### 文本分割
- instructor <font color="red">ok</font>
- llamahub(LlamaIndex) <font color="red">ok</font>
- unstructured.io <font color="orange">pass</font>
### 分块策略(SentenceSplitter??)
- 基于token分块 <font color="red">ok</font>
- 递归分块 <font color="red">ok</font>
- 语义分块 <font color="red">ok</font>
### <font color="orange">多查询</font>
### 检索增强
#### 重排序
- bge rerank <font color="red">ok</font>
- cohere rerank <font color="orange">pass</font>
####  <font color="orange">混合检索</font>
- dpr <font color="orange">pass</font>
- colbert <font color="orange">pass</font>

### <font color="orange">统一语义空间</font>
- superlinked <font color="orange">pass</font>
### 知识图谱
- neo4j <font color="red">ok</font>
- grakn <font color="orange">pass</font>
- wikibase <font color="orange">pass</font>

### 可观测性-监控和调试rag管道
- arize ai
- whylabs
- langsmith

我看有人发帖介绍ai相关的技术栈，内容如下。值得学习吗？有什么用？哪个在日本ai业界比较流行？你有什么看法，


### 工作流编排
- beam ai
- modal
- prefect marvin
- bentoml

### 评估rag系统性能
- ragas <font color="red">ok</font>
- giskard <font color="orange">pass</font>
- trulens <font color="orange">pass</font>

### 
- lora
- 微调
- use local llm to use neo4j