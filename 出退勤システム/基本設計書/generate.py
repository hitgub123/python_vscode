from google import genai
import os

def get_ai_client():
    api_key=os.environ.get("ceria_gemini_api_key")
    client = genai.Client(api_key=api_key)
    return client

def genereate_contents(input):
    sample_content="ssssssss"
    with open(f"{os.getcwd()}/基本設計書/基本設計書_req-001_出退勤打刻.md", "r",encoding='utf-8') as f:
        sample_content = f.read()
    content = f"""
    你是日本某出退勤系统的项目经理，请根据输入编写基本设计书。
    要求用日语生成md格式，遵循日本it行业规范，件格式参考:
    参考文件start:
    {sample_content}
    参考文件end:
    注意：
    1，每个标题都不要带4.1,4.2这样的标号。
    2，处理里的异常部分用红色字体。
    输入是{input}
    """

    return content

def save(content,finename):
    with open(f"{os.getcwd()}/基本設計書/基本設計書_{finename}.md", "w",encoding='utf-8') as f:
        f.write(content)

def main():
    list_=get_list()
    for o in list_:
        input = o
        if input["id"]!="req-017":
            continue
        print(input)
        client=get_ai_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=genereate_contents(input),
        )
        # print(response.text)
        save(response.text, input["id"])

def get_list():
    list_=[]
    with open(
        f"{os.getcwd()}/files/業務要件一覧.txt",
        "r",
        # encoding="utf-8",
    ) as f:
        for i in f.readlines():
            # id,分類,要件名,概要,利用者=i.split('\t')
            id,分類,要件名,概要,利用者=i.split('\t')
            # print(id, 分類, 要件名, 概要, 利用者)
            list_.append(
                {
                    "id": id,
                    "分類": 分類,
                    "要件名": 要件名,
                    "概要": 概要,
                    "利用者": 利用者,
                }
            )
    list_.pop(0)
    return list_
if __name__=="__main__":
    # print(get_list())
    main()
