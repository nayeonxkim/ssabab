import requests
import json
import base64

url = 'http://meeting.ssafy.com/api/v4/posts'

headers = {
    'Content-Type': 'application/json'
}
# image_path = './cap1.png'

# with open(image_path, 'rb') as f:
#     image_data = f.read()
#     image_base64 = base64.b64encode(image_data).decode('utf-8')

data = {
  "channel_id": "#kny_test",
  "message": "string",
  "root_id": "string",
  "file_ids": [
    "string"
  ],
  "props": {},
  "metadata": {
    "priority": {
      "priority": "string",
      "requested_ack": True
    }
  }
}


response = requests.post(url, headers=headers, data=json.dumps(data))

# 응답 확인
print(response.status_code)
print(response.text)
