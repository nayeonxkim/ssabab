# 환경변수
import os
from dotenv import load_dotenv

# 시간 설정
from pytz import timezone
from datetime import datetime

# 크롤링
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# 이미지 처리
from PIL import Image, ImageFont, ImageDraw

# webhook 통신
import json
import requests

# base64 인코딩 디코딩
import io
import base64

# AWS S3 세팅
import boto3

def s3_connection():
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name = "s3",
            region_name = "ap-northeast-2",
            aws_access_key_id = os.environ.get('aws_access_key_id'),
            aws_secret_access_key = os.environ.get('aws_secret_access_key'),
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!") 
        return s3

def image2base64(img):
    buffer = io.BytesIO()
    img.save(buffer, 'jpeg')
    return 'data:image/jpeg;base64,'+ base64.b64encode(buffer.getvalue()).decode("utf-8")

def merge_SS_in_a_column(SS_arr):
    width = SS_arr[0].size[0]
    height = 0
    for SS in SS_arr: height += SS.size[1]
    
    merged_SS = Image.new('RGB', (width,  height), (255, 255, 255))

    y = 0
    for SS in SS_arr:
        merged_SS.paste(SS, (0, y))
        y += SS.size[1]

    return merged_SS

def merge_SS_in_a_row(SS_arr):
    width = 0
    height = 0
    for SS in SS_arr: 
        width += SS.size[0]
        if height < SS.size[1]:
            height = SS.size[1]
    
    merged_SS = Image.new('RGB', (width,  height), (255, 255, 255))

    x = 0
    for SS in SS_arr:
        merged_SS.paste(SS, (x, 0))
        x += SS.size[0]

    return merged_SS

def add_text_on_SS(img, text, fontsize=100):
    width, height = img.size
    new_SS = Image.new('RGB', (width,  height+fontsize), (255, 255, 255))
    new_SS.paste(img, (0, fontsize))
    draw =ImageDraw.Draw(new_SS)
    font = ImageFont.truetype("Happiness-Sans-Bold.ttf", 72, encoding="UTF-8")
    draw.text((0, 0),text, fill="black", font=font)

    return new_SS

def get_eating_first():
    day = datetime.strptime("20230710", "%Y%m%d")
    today = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d")
    today = datetime.strptime(today, "%Y%m%d")
    Q = (today-day).days//7
    R = (today-day).days%7
    return (R%2+Q%2)%2+1

class SSABOB():
    config = {
        'menuDt' : None,
        'username' : None,
        'password' : None,
        'cookie' : None,
        'incoming_webhook_url': None,

        'menuCourseTypes' : ["AA", "BB", "CC", "DD", "EE"],
        'menuMealType': 2,  # 중식
        'hallNo': 'E32',
        'restaurantCode': 'REST000595',  # 전기부산
    }

    def __init__(self, config=dict()):
        self.config['menuDt'] = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d")
        self.set_config(config)

    def set_config(self, config):
        self.config = dict(self.config, **config)

    def initialize_webdriver(self):
        # Chrome 웹드라이버 경로 설정
        webdriver_service = Service('path/to/chromedriver')
        # webdriver_service = Service('/opt/chrome/chromedriver')

        # Chrome 웹드라이버 옵션 설정
        options = Options()
        options.add_experimental_option("mobileEmulation", { "deviceName": "Samsung Galaxy S20 Ultra" })   # 모바일 화면 설정
        options.add_argument('--headless')  # 브라우저 창을 띄우지 않고 실행
        options.add_argument('--no-sandbox')
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
        options.add_argument('window-size=1392x1150')
        options.add_argument("disable-gpu")

        # Chrome 웹드라이버 객체 생성
        self.driver = webdriver.Chrome(service=webdriver_service, options=options)

    def login_by_username(self):
        # 로그인 페이지 URL
        login_url = "https://welplus.welstory.com/#/login/username"

        # 로그인 페이지로 이동
        self.driver.get(login_url)
        
        # 로그인 페이지 로딩 대기
        WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.ID, "wrtId")))

        # 사용자 이름 입력
        username_input = self.driver.find_element(By.ID, "wrtId")
        username_input.send_keys(self.config['username'])

        # 비밀번호 입력
        password_input = self.driver.find_element(By.ID, "wrtPw")
        password_input.send_keys(self.config['password'])

        # 로그인 버튼 클릭
        login_button = self.driver.find_element(By.CSS_SELECTOR, "#contents > div > form > div.btn-wrap > button")
        login_button.click()

    def login_by_cookie(self):
        # 로그인 페이지 URL
        login_url = "https://welplus.welstory.com/#/login/username"

        # 로그인 페이지로 이동
        self.driver.get(login_url)

        # 쿠키 설정
        cookie = {'name' : 'remember-me', 'value' : self.config['cookie']}  
        self.driver.add_cookie(cookie)      

    def capture_a_menu(self, menuCourseType):
        
        # 크롤링할 웹페이지의 URL
        target_url = f"https://welplus.welstory.com/#/meal/detail?menuDt={self.config['menuDt']}&hallNo={self.config['hallNo']}M&menuCourseType={menuCourseType}&menuMealType={self.config['menuMealType']}&restaurantCode={self.config['restaurantCode']}"

        # hash router로 인해
        # params만 바뀌는 경우 페이지가 변경되지 않기 떄문에
        # 다른 페이지를 경유해서 리프레시 시켜줌
        self.driver.get("https://welplus.welstory.com/main")

        # 크롤링할 페이지로 이동
        self.driver.get(target_url)

        # 메뉴 썸네일 로딩 대기
        WebDriverWait(self.driver, 2).until(expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, "#contents > div.meal-details-top > div > div")
        ))
        thum = self.driver.find_element(By.CSS_SELECTOR, "#contents > div.meal-details-top > div > div")
        while 'https://samsungwelstory.com/data/manager/recipe/' not in thum.value_of_css_property("background-image"):
            print("이미지 로딩 대기 중")
            thum = self.driver.find_element(By.CSS_SELECTOR, "#contents > div.meal-details-top > div > div")

        # 메뉴 썸네일 및 메뉴이름 & 영양정보 캡처
        meal_card = self.driver.find_element(By.CSS_SELECTOR, "#contents > div.meal-details-view > div.details-meal-item-card")
        meal_card_SS = Image.open(io.BytesIO(meal_card.screenshot_as_png))
        thum_SS = Image.open(io.BytesIO(thum.screenshot_as_png))  # 안정적인 캡처를 위해 조금 늦게 캡처

        # 상세메뉴 & 칼로리 캡처
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # 스크롤 끝까지 내리기
        details = self.driver.find_element(By.CSS_SELECTOR, "#tab-0")
        details_SS = Image.open(io.BytesIO(details.screenshot_as_png))

        return merge_SS_in_a_column([thum_SS, meal_card_SS, details_SS])

    def capture_all_menu(self):
        self.initialize_webdriver()

        if self.config.get("cookie"): self.login_by_cookie()
        else: self.login_by_username()

        menu_screenshots = [self.capture_a_menu(mct) for mct in self.config['menuCourseTypes']]

        self.driver.quit()
        
        return merge_SS_in_a_row(menu_screenshots)

    def handle_incoming_webhook(self, img_url):
        headers = {'Content-Type': 'application/json',}
        data = json.dumps({
            "attachments": [{
                "image_url": img_url
            }]
        })

        requests.post(self.config['incoming_webhook_url'], headers=headers, data=data)
        print("완료")

if __name__ == '__main__':
    load_dotenv()
    config = {
        # 로그인 정보
        'username': os.environ.get('SSABOB_USERNAME'),
        'password': os.environ.get('SSABOB_PASSWORD'),
        # 쿠키 정보
        'cookie':os.environ.get('SSABOB_COOKIE'),
        'incoming_webhook_url':os.environ.get('INCOMING_WEBHOOK_URL'),
    }
    app = SSABOB(config)
    
    def loop(cnt, current=0):
        if cnt == current: raise Exception('app 작동 실패')
        print(f"app 실행 - {current}")

        try:
            screenshot = app.capture_all_menu()
            print("app 작동 완료")
            return screenshot
        except:
            return loop(cnt, current+1) 

    screenshot = loop(10)
    
    screenshot = add_text_on_SS(screenshot, f"{get_eating_first()}반 먼저")
    screenshot.save('todayMenu.png')

    s3 = s3_connection()
    today = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d")
    try:
        s3.upload_file("todayMenu.png", os.environ.get('aws_bucket'),f"{today}.png")
    except Exception as e:
        print(e)

    # img_url = image2base64(screenshot)
    img_url = os.environ.get('aws_img_url')+f"{today}.png"
    app.handle_incoming_webhook(img_url)
