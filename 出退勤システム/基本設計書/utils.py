from google import genai
import os

api_key=os.environ.get("ceria_gemini_api_key")
client = genai.Client(api_key=api_key)


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
    input = """
    {id:req-016,
	分類:残業管理,
		要件名：部下残業実績確認，
			概要:管理職は、自身の部下の残業時間実績を月次で確認し、適切な労働時間管理を行える。,
				利用者:管理職, 人事部門}
                """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=genereate_contents(input),
    )

    # print(response.text)
    save(response.text, "req-016")

if __name__=="__main__":
    # print(genereate_contents())
    main()
