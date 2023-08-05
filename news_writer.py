from tistory_util import *
import requests
from typing import List
import asyncio
from concurrent.futures import ProcessPoolExecutor
import datetime
import pynecone as pc
import requests
from bs4 import BeautifulSoup
import pandas as pd
from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import SystemMessage

from langchain.utilities import DuckDuckGoSearchAPIWrapper
import tiktoken
import os
import openai

#openai.api_key = os.environ["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"]
openai.api_key = "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"

###########################################################
# Helpers
def build_summarizer(llm):
    system_message = "assistant는 user의 내용을 bullet point 3줄로 요약하라. 영어인 경우 한국어로 번역해서 요약하라."
    system_message_prompt = SystemMessage(content=system_message)

    human_template = "{text}\n---\n위 내용을 bullet point로 3줄로 한국어로 요약해"
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt,
                                                    human_message_prompt])

    chain = LLMChain(llm=llm, prompt=chat_prompt)
    return chain


def truncate_text(text, max_tokens=3000):
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:  # 토큰 수가 이미 3000 이하라면 전체 텍스트 반환
        return text
    return enc.decode(tokens[:max_tokens])


def clean_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join(soup.stripped_strings)
    return text


def task(search_result):
    title = search_result['title']
    url = search_result['link']
    snippet = search_result['snippet']

    content = clean_html(url)
    full_content = f"제목: {title}\n발췌: {snippet}\n전문: {content}"

    full_content_truncated = truncate_text(full_content, max_tokens=3500)

    summary = summarizer.run(text=full_content_truncated)

    result = {"title": title,
              "url": url,
              "content": content,
              "summary": summary
              }

    return result


###########################################################
# Instances
llm = ChatOpenAI(temperature=0.8)

search = DuckDuckGoSearchAPIWrapper()
search.region = 'kr-kr'
#enc = tiktoken.get_encoding("cl100k_base")
enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

summarizer = build_summarizer(llm)


###########################################################
# Web

class Data(pc.Model, table=True):
    """A table for questions and answers in the database."""

    title: str
    content: str
    url: str
    summary: str
    timestamp: datetime.datetime = datetime.datetime.now()


class State(pc.State):
    """The app state."""

    is_working: bool = False
    columns: List[str] = ["title", "url", "summary"]
    topic: str = ""

    async def handle_submit(self):
        self.is_working = True
        yield

        topic = self.topic

        search_results = search.results(topic, num_results=10)

        with ProcessPoolExecutor() as executor:
            with pc.session() as session:

                for s in search_results:
                    # {"title":~~~, "snippet":~~, "link":~~~}
                    s = await asyncio.get_running_loop().run_in_executor(executor, task, s)
                    record = Data(title=s['title'],
                                  content=s['content'],
                                  url=s['url'],
                                  summary=s['summary'])
                    session.add(record)
                    session.commit()
                    yield

        self.is_working = False

    @pc.var
    def data(self) -> List[Data]:
        """Get the saved questions and answers from the database."""
        with pc.session() as session:
            samples = (
                session.query(Data)
                .order_by(Data.timestamp.asc())
                .all()
            )
            return [[s.title, s.url, s.summary] for s in samples]

    def export(self):
        with pc.session() as session:
            samples = (
                session.query(Data)
                .all()
            )
            d = [{"title": s.title,
                  "url": s.url,
                  "summary": s.summary,
                  "content": s.content} for s in samples]

            df = pd.DataFrame(d)
            df.to_excel("./exported.xlsx")

    def delete_all(self):
        with pc.session() as session:
            samples = (
                session.query(Data)
                .all()
            )

            for s in samples:
                session.delete(s)
            session.commit()


def index() -> pc.Component:
    return pc.center(
        pc.vstack(
            pc.heading("뉴스 크롤링 & 요약 서비스", font_size="2em"),
            pc.input(placeholder="topic", on_blur=State.set_topic),
            pc.hstack(
                pc.button("시작", on_click=State.handle_submit),
                pc.button("excel로 export", on_click=State.export),
                pc.button("모두 삭제", on_click=State.delete_all),
            ),
            pc.cond(State.is_working,
                    pc.spinner(
                        color="lightgreen",
                        thickness=5,
                        speed="1.5s",
                        size="xl",
                    ),),
            pc.data_table(
                data=State.data,
                columns=State.columns,
                pagination=True,
                search=True,
                sort=False,
            ),
            width="80%",
            font_size="1em",
        ),
        padding_top="10%",
    )


# Add state and page to the app.
#app = pc.App(state=State)
#app.add_page(index)
#app.compile()


nasa_url = "https://api.nasa.gov/planetary/apod?api_key=rP3Xf5YvfJhYXyRHGVPtQkyJvof3TbqbKiUuuWBd"
def writer():

    data_from_nasa = requests.get(nasa_url).json()


    search_results = search.results("속보", num_results=10)
    i = 0
    record=[0,0,0,0,0,0,0,0,0,0]
    for s in search_results:
       # record[i] = Data(title=s['title'],content=s['content'],url=s['url'],summary=s['summary'])
        #record[i] = s

        content = clean_html(s['link'])
        full_content = f"제목: {s['title']}\n발췌: {s['snippet']}\n전문: {content}"

        full_content_truncated = truncate_text(full_content, max_tokens=3500)

        summary = summarizer.run(text=full_content_truncated)

        record[i] = {"title": s['title'],
                  "url": s['link'],
                  "content": content,
                  "summary": summary
                  }
        i=i+1





    title2 = f"오늘의 속보 뉴스! 심층분석 ({data_from_nasa['date']})"

    content2 = f'''
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br />
<span style="font-family: 'Noto Serif KR';">안녕하세요, 오늘의 뉴스 속보는 어떤 것들이 있을까요?!<br/> 
오늘의 HOT한 뉴스만 정리했습니다<br />
링크도 있으니 함께 보시죠!</span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[0]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[0]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[0]['content']} </br>{record[0]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[1]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[1]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[1]['content']} </br>{record[1]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[2]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[2]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[2]['content']} </br>{record[2]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[3]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[3]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[3]['content']} </br>{record[3]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[4]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[4]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[4]['content']} </br>{record[4]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[5]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[5]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[5]['content']} </br>{record[5]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[6]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[6]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[6]['content']} </br>{record[6]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[7]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[7]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[7]['content']} </br>{record[7]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[8]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[8]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[8]['content']} </br>{record[8]['url']}  </span></p>
<p>&nbsp;</p>

<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style3" />
<h3 style="text-align: center;" data-ke-size="size23"><br /><span style="font-family: 'Noto Serif KR';"><b>{record[9]['title']} </b></span></h3>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[9]['summary']}  </span></p>
<p>&nbsp;</p>
<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br /><span style="font-family: 'Noto Serif KR';">
 </br>{record[9]['content']} </br>{record[9]['url']}  </span></p>
<p>&nbsp;</p>



<p style="text-align: center;" data-ke-size="size16"><span style="font-family: 'Noto Serif KR';"> </span><br />
<span style="font-family: 'Noto Serif KR';">오늘도 이슈가 많은 하루였네요.<br />
저는 내일도 새로운 뉴스 속보를 가지고 오겠습니다., 편안한 하루 보내세요!</span></p>
<p>&nbsp;</p>
            '''

    return title2, content2


if __name__ == "__main__":
    title2, content2 = writer()

    blog_write(
        blog_name="honeybutterinfo",
        category_id="953967",
        title="[뉴스/시사]"+title2,
        content=content2,
        tag='속보, 뉴스'
    )