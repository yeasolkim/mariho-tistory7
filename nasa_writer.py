from tistory_util import *
import requests
from googletrans import Translator


class Google_Translator:
    def __init__(self):
        self.translator = Translator()
        self.result = {'src_text': '', 'src_lang': '', 'tgt_text': '', 'tgt_lang': ''}

    def translate(self, text, lang='en'):
        translated = self.translator.translate(text, dest=lang)
        self.result['src_text'] = translated.origin
        self.result['src_lang'] = translated.src
        self.result['tgt_text'] = translated.text
        self.result['tgt_lang'] = translated.dest

        return self.result

    def translate_file(self, file_path, lang='en'):
        with open(file_path, 'r') as f:
            text = f.read()
        return self.translate(text, lang)
blog_name = "honeybutterinfo"
category_id = "953967"  # APOD
nasa_url = "https://api.nasa.gov/planetary/apod?api_key=rP3Xf5YvfJhYXyRHGVPtQkyJvof3TbqbKiUuuWBd"
translator = Google_Translator()
def writer():

    data_from_nasa = requests.get(nasa_url).json()

    result = translator.translate(data_from_nasa['explanation'], 'ko')

    title = f"NASA 우주 핫이슈! ({data_from_nasa['date']})"

    content = f'''
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br />
<span style="font-family: 'Noto Serif KR';">안녕하세요, 우주는 넓고 우리는 먼지같은 존재라고들 하는데요!<br/> 
오늘은 NASA에서 어떤 우주의 모습을 비춰줄까요?<br />
먼저 사진부터 감상하시죠!</span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>PHOTO</b></span></h3>

<p><img src="{data_from_nasa['url']}" /></p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br />
<span style="font-family: 'Noto Serif KR';">이 사진의 제목은 <span>{data_from_nasa['title']}</span> 입니다. NASA에서 공식적으로 제공한 설명을 보시죠.</span></p>
<p>&nbsp;</p>
<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>설명 [English.ver]</b></span></h3>

<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">{result['src_text']}</span></span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>설명 [Korean.ver]</b></span></h3>

<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">{result['tgt_text']}</span></span></p>

<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br />
<span style="font-family: 'Noto Serif KR';">우주나 천문학 관련 사진을 보면 정말 놀랍습니다.<br />
저는 내일도 새로운 경이로운 우주소식과 함께 돌아오겠습니다, 여러분도 오늘 멋진 하루를 여행하세요!</span></p>
<p>&nbsp;</p>
            '''

    return title, content


if __name__ == "__main__":
    title, content = writer()

    blog_write(
        blog_name=blog_name,
        category_id=category_id,
        title="[우주/천문]"+title,
        content=content,
        tag='NASA, 천문학, 우주, 우주이슈, 나사, 망원경, 천체, 행성, 항성, 태양계, 외계'
    )