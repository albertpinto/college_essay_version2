import requests

url = 'http://localhost:8000/stream_college_essay'
response = requests.get(url, stream=True)

for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        print(decoded_line)