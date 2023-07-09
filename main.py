import time
import io
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image

# Chrome 웹드라이버 경로 설정
webdriver_service = Service('path/to/chromedriver')

# Chrome 웹드라이버 옵션 설정
options = Options()
options.add_experimental_option("mobileEmulation", { "deviceName": "iPhone X" })   # 모바일 화면 설정
# options.add_argument('--headless')  # 브라우저 창을 띄우지 않고 실행

# Chrome 웹드라이버 객체 생성
driver = webdriver.Chrome(service=webdriver_service, options=options)

def login_by_username():
    # 로그인 페이지 URL
    login_url = "https://welplus.welstory.com/#/login/username"

    # 로그인 정보
    username = ""
    password = ""

    # 로그인 페이지로 이동
    driver.get(login_url)


    # 로그인 페이지 로딩 대기
    time.sleep(1)


    # 사용자 이름 입력
    username_input = driver.find_element(By.ID, "wrtId")
    username_input.send_keys(username)

    # 비밀번호 입력
    password_input = driver.find_element(By.ID, "wrtPw")
    password_input.send_keys(password)

    # 로그인 버튼 클릭
    login_button = driver.find_element(By.CSS_SELECTOR, "#contents > div > form > div.btn-wrap > button")
    login_button.click()

    # 로그인이 완료될 때까지 대기
    time.sleep(1)

def login_by_cookie():
    
    # 로그인 페이지 URL
    login_url = "https://welplus.welstory.com/#/login/username"

    # 로그인 페이지로 이동
    driver.get(login_url)
    time.sleep(0.1)

    # 쿠키 정보
    cookie = {'name' : 'remember-me', 'value' : ''}  

    # 쿠키 설정
    driver.add_cookie(cookie)      

# login_by_username()
login_by_cookie()

# menuDt = '20230708'
menuDt = datetime.now().strftime("%Y%m%d")

def merge_SS_in_a_column(SS_arr):
    width = SS_arr[0].size[0]
    height = 0
    for SS in SS_arr: height += SS.size[1]
    
    full_SS = Image.new('RGB', (width,  height), (255, 255, 255))

    y = 0
    for SS in SS_arr:
        full_SS.paste(SS, (0, y))
        y += SS.size[1]

    # full_SS.show()
    return full_SS

def merge_SS_in_a_row(SS_arr):
    width = 0
    height = 0
    for SS in SS_arr: 
        width += SS.size[0]
        if height < SS.size[1]:
            height = SS.size[1]
    
    full_SS = Image.new('RGB', (width,  height), (255, 255, 255))

    x = 0
    for SS in SS_arr:
        full_SS.paste(SS, (x, 0))
        x += SS.size[0]

    # full_SS.show()
    return full_SS

def capture_a_menu(menuCourseType):
    # 크롤링할 웹페이지의 URL
    target_url = f"https://welplus.welstory.com/#/meal/detail?menuDt={menuDt}&hallNo=E32M&menuCourseType={menuCourseType}&menuMealType=2&restaurantCode=REST000595"

    # params만 바뀌는 경우
    # 페이지가 변경되지 않기 떄문에
    # meal 페이지를 경유해서 리프레시 시켜줌
    driver.get("https://welplus.welstory.com/#/meal")
    time.sleep(0.1)

    # 크롤링할 페이지로 이동
    driver.get(target_url)
    time.sleep(1)

    # 메뉴 썸네일 캡처
    thum = driver.find_element(By.CSS_SELECTOR, "#contents > div.meal-details-top > div > div")
    thum_SS = Image.open(io.BytesIO(thum.screenshot_as_png))

    # 메뉴이름 & 영양정보 캡처
    meal_card = driver.find_element(By.CSS_SELECTOR, "#contents > div.meal-details-view > div.details-meal-item-card")
    meal_card_SS = Image.open(io.BytesIO(meal_card.screenshot_as_png))

    # 상세메뉴 & 칼로리 캡처
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # 스크롤 끝까지 내리기
    details = driver.find_element(By.CSS_SELECTOR, "#tab-0")
    details_SS = Image.open(io.BytesIO(details.screenshot_as_png))

    return merge_SS_in_a_column([thum_SS, meal_card_SS, details_SS])

def capture_all_menu():
    SS_arr = []
    menuCourseTypes = ["AA", "BB", "CC", "DD", "EE"]
    for menuCourseType in menuCourseTypes:
        SS_arr.append(capture_a_menu(menuCourseType))
    
    merge_SS_in_a_row(SS_arr).save("todayMenu.png","PNG")

capture_all_menu()

# 웹드라이버 종료
driver.quit()
