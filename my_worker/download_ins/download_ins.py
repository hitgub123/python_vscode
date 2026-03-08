from playwright.sync_api import sync_playwright
import time
import requests,os

download_path='my_worker/download_ins/download/'

def download_chk(page):
    # ==================== 等待用户输入 ====================
    # if 'img_index' not in page.url:
    #     return False
    user_input = input("当前帖子就绪 → 输入任意内容下载，否则跳过: ").strip().lower()
    if user_input:
        return True
    return False

def download_img(url,filepath):
    resp = requests.get(url, timeout=20)
    if resp.status_code == 200:
        # ext = ".mp4" if "video" in media.evaluate("el=>el.tagName") else ".jpg"
        ext='.jpg'
        filename = f"{time.time()}{ext}"
        fullfilename = os.path.join(filepath, filename)
        with open(fullfilename, "wb") as f:
            f.write(resp.content)
        print(f"直接下载成功 → {fullfilename}")
    else:
        print("直链下载失败", resp.status_code)

def get_folder_name(a):
    a=a[a.find('/p/')+3:]
    b=a.find('/')
    if b!=-1:
        a=a[:b]    
    return a
def download_by_tag(page):
    folder_name=get_folder_name(page.url)
    folder_path = os.path.join(download_path, folder_name)          # 可以是相对路径或绝对路径
    os.makedirs(folder_path, exist_ok=True)   # 自动创建多级目录，不存在才创建，已存在不报错

    article = page.locator('article').first
    urls=[]
    while 1:
        images = article.locator('div._aagv img[src^="https://"]').all()
        # images = article.locator("img").all()

        for image in images:
            url=image.get_attribute('src')
            if url not in urls:
                print(url)
                urls.append(url)
                download_img(url,folder_path)

        next_pic_btn = article.locator('button._afxw div._9zm2')
        try:
            next_pic_btn.wait_for(state="visible", timeout=3000)
            next_pic_btn.click()
            time.sleep(2)
        except Exception as e:
            print("没找到下一个按钮（或超时） →", str(e))
            return

def download_by_btn(page):
    print("正在点击下载按钮...")
    # ↓↓↓ 你提供的下载按钮精确 selector ↓↓↓
    download_btn = page.locator('div[title="Download images/videos."] button')
    download_btn=download_btn.last
    download_btn.wait_for(state="visible", timeout=10000)
    download_btn.click()

def main():
    with sync_playwright() as p:
        # 连接你已经打开的 Edge（必须先用 --remote-debugging-port=9222 启动）
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        
        # 自动找到 Instagram 页面（更稳妥）
        page = None
        for pg in context.pages:
            if "instagram.com" in pg.url.lower():
                page = pg
                break
        if not page:
            page = context.pages[0]
        
        print("✅ 已成功接管浏览器，开始自动化！")
        print("操作提示：输入 'ok' 下载当前帖子，其它任意字符跳过，输入 'q' 退出脚本\n")


        while True:
            try:

                download_flg=download_chk(page)
                if download_flg:
                    # download_by_btn(page)
                    download_by_tag(page)
                    
                    print("✅ 下载已触发，等待所有图片/视频下载完成...")
                    page.wait_for_timeout(2000)   # ← 关键！给插件足够时间（图片越多可改大：15000~20000）
                    print("当前帖子下载完成！")
                else:
                    print("已跳过当前帖子")

                # ==================== 点击右箭头进入下一个 ====================
                print("正在切换到下一个帖子...")
                # ↓↓↓ 你提供的右箭头精确 selector ↓↓↓
                next_btn = page.locator('div._aaqg._aaqh button._abl-')
                next_btn.wait_for(state="visible", timeout=8000)
                next_btn.click()
                
                # 等待新帖子加载完成
                page.wait_for_timeout(1000)
                print("已进入下一个帖子，准备就绪\n")

            except Exception as e:
                print(f"⚠️ 操作失败或已没有下一个帖子了: {e}")
                retry = input("输入 'r' 重试当前步骤，或直接回车退出: ").strip().lower()
                if retry != "r":
                    break

        # 结束
        browser.close()
        print("浏览器连接已关闭，脚本结束。")

if __name__ == "__main__":
    main()