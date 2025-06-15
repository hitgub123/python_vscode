from google import genai
import os
from configuration import generation_config


def get_ai_client():
    api_key = os.environ.get("ceria_gemini_api_key")
    client = genai.Client(api_key=api_key)
    return client


def genereate_contents(input):
    sample_content = ""
    sample_file = f"{os.getcwd()}/基本設計書_機能要件/基本設計書_fun-001_出勤打刻機能.md"
    if os.path.exists(sample_file):
        with open(
            sample_file,
            "r",
            encoding="utf-8",
        ) as f:
            sample_content = f.read()
    content = f"""
    你是日本某出退勤系统的项目经理,
    请根据输入编写基本设计书。
    要求用日语生成md格式，遵循日本it行业规范，件格式参考:
    参考文件start:
    {sample_content}
    参考文件end:
    注意：
    1，每个标题都不要带4.1,4.2这样的标号。
    2，处理里的异常部分用红色字体。
    3，在一个机能文件里不要写别的机能的内容。
    4，只输出文件内容，不要写 START OF FILE 或者end of file这些跟机能无关的东西。
    5,不要输出 ```md这样的内容
    6，ID，分類，機能名，概要，利用者，作成者、作成日付这些信息用一个表格输出
    7，出现分支都用表格输出，比如业务上的判断
    8，修改入力的写法，分成两部分，第一部分是入力项目，里面写[項目]，[内容]，[型]，[必須]，[備考]，
    第二部分写业务check逻辑，比如取值范围，但不要和第一部分的必須和型的内容重复。
    9，尽可能的多用表格式写，比如入力项目，业务check，出力项目
    10，処理詳細里不要写check，因为在[入力]里已经写了
    输入是{input}
    """

    return content


def save(content, finename):
    with open(
        f"{os.getcwd()}/基本設計書_機能要件/基本設計書_{finename}.md",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(content)


def main():
    list_ = get_list()
    for input in list_:
        if input["id"] < "fun-008":            continue
        # if input["id"] > "fun-002":            return
        print(input)
        client = get_ai_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            # system_instruction="你是日本某出退勤系统的项目经理",
            config=generation_config,
            contents=genereate_contents(input),
        )
        # print(response.text)
        save(response.text, f'{input["id"]}_{input["機能名"]}')


def get_list():
    list_ = []
    with open(
        f"{os.getcwd()}/files/機能要件一覧.txt",
        "r",
        # encoding="utf-8",
    ) as f:
        for i in f.readlines():
            # id	分類	機能名	概要	入力	出力	利用者=i.split('\t')
            id, 分類, 機能名, 概要, 入力, 出力, 利用者 = i.split("\t")
            # print(id, 分類, 機能名, 概要, 入力, 出力, 利用者)
            list_.append(
                {
                    "id": id,
                    "分類": 分類,
                    "機能名": 機能名,
                    "概要": 概要,
                    "入力": 入力,
                    "出力": 出力,
                    "利用者": 利用者,
                }
            )
    list_.pop(0)
    return list_


if __name__ == "__main__":
    # print(get_list())
    main()
