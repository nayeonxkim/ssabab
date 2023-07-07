import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Chrome 웹드라이버 경로 설정
webdriver_service = Service('path/to/chromedriver')

# Chrome 웹드라이버 옵션 설정
options = Options()
# options.add_argument('--headless')  # 브라우저 창을 띄우지 않고 실행

# Chrome 웹드라이버 객체 생성
driver = webdriver.Chrome(service=webdriver_service, options=options)

# 로그인 페이지 URL
login_url = "https://welplus.welstory.com/#/login/username"

# 로그인 정보
username = ""
password = ""

# 로그인 페이지로 이동
driver.get(login_url)


# 로그인 페이지 로딩 대기
time.sleep(3)


# 사용자 이름 입력
username_input = driver.find_element(By.ID, "wrtId")
username_input.send_keys(username)

# 로그인 페이지 로딩 대기
time.sleep(3)

# 비밀번호 입력
password_input = driver.find_element(By.ID, "wrtPw")
password_input.send_keys(password)

# 로그인 페이지 로딩 대기
time.sleep(3)

# 로그인 버튼 클릭
login_button = driver.find_element('button')
login_button.click()

# 로그인이 완료될 때까지 대기
time.sleep(5)

# 크롤링할 웹페이지의 URL
target_url = "https://welplus.welstory.com/#/meal/detail?menuDt=230707&hallNo=E32M&menuCourseType=BA&menuMealType=2&restaurantCode=REST000595"

# 크롤링할 페이지로 이동
driver.get(target_url)

# 웹 화면 캡처
driver.save_screenshot('C:/Users/SSAFY/Desktop/ssabab/cap1.png')

# 웹드라이버 종료
driver.quit()
