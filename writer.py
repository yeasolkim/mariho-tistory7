from tistory_util import *
import requests


blog_name = "honeybutterinfo"
category_id = "953967"  # APOD
#nasa_url = "https://api.nasa.gov/planetary/apod?api_key=YOUR_KEY"


def writer():



    title = f"혈당 관리 하는 법"

    content = f'''
<p><span style="color: #000000;">안녕하세요. 올해 주식장의 전체적인 흐름은 어떨까요?</span><span style="color: #000000;"><br /></span>
<span style="color: #000000;">먼저 그래프부터 확인하시죠!</span></p>
<p><span style="color: #000000;">여러분은 오늘 어떤 하루를 보내셨나요? 저는 내일의 주가로 다시 돌아오겠습니다.</span><span style="color: #000000;"><br /></span>
<p>&nbsp;</p>
            '''

    return title, content


if __name__ == "__main__":
    title, content = writer()

    blog_write(
        blog_name=blog_name,
        category_id=category_id,
        title=title,
        content=content,
        tag='급등주, 단타'
    )