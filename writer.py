from tistory_util import *
import requests
from datetime import datetime, timedelta
from PublicDataReader import TransactionPrice
# 시군구코드 조회하기
import PublicDataReader as pdr
blog_name = "honeybutterinfo"
category_id = "953967"  # APOD
#nasa_url = "https://api.nasa.gov/plane.tary/apod?api_key=rP3Xf5YvfJhYXyRHGVPtQkyJvof3TbqbKiUuuWBd"


def writer():
    service_key = "0D0HtvRO%2BWh1IFcXpUuhlNnYZIBjPWChwnecrxRqLKdyxz8wFx9J%2B6st65NQWJAWNyvOJ3b%2B2lyPkC5FQhLGdw%3D%3D"
    api = TransactionPrice(service_key)
    sigungu_name = "분당구"
    code = pdr.code_bdong()
    code.loc[(code['시군구명'].str.contains(sigungu_name)) &
             (code['읍면동명'] == '')]

    # 특정 년월 자료만 조회하기
    df1 = api.get_data(
        property_type="아파트",
        trade_type="매매",
        sigungu_code="41135",
        year_month="202212",
    )

    # 특정 기간 자료 조회하기
    df2 = api.get_data(
        property_type="아파트",
        trade_type="매매",
        sigungu_code="41135",
        start_year_month="202212",
        end_year_month="202301",
    )

    start_date = (datetime.now()).strftime('%Y-%m-%d')
    title = f"혈당 관리 하는 법({start_date})"

    content = f'''
<p><span style="color: #000000;">안녕하세요. 올해 주식장의 전체적인 흐름은 어떨까요?</span>
<span style="color: #000000;"><br /></span>
<span style="color: #000000;">먼저 그래프부터 확인하시죠!{df1} </span>{df2}</p>
<p><span style="color: #000000;">여러분은 오늘 어떤 하루를 보내셨나요? 저는 내일의 주가로 다시 돌아오겠습니다.</span>
<span style="color: #000000;"><br /></span>
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
        tag='아파트 실거래가'
    )