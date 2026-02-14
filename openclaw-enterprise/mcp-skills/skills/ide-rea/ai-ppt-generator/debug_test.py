import os
import sys
import requests
import json

api_key = os.getenv('BAIDU_API_KEY')
print(f"API Key present: {bool(api_key)}")

# 测试获取PPT主题
url = "https://qianfan.baidubce.com/v2/tools/ai_ppt/get_ppt_theme"
headers = {
    "Authorization": f"Bearer {api_key}",
}

print("\n=== Testing get_ppt_theme ===")
response = requests.post(url, headers=headers)
print(f"Status Code: {response.status_code}")
result = response.json()
print(f"Result keys: {list(result.keys())}")

if 'data' in result:
    data = result['data']
    print(f"Data keys: {list(data.keys())}")
    if 'ppt_themes' in data:
        themes = data['ppt_themes']
        print(f"Number of themes: {len(themes)}")
        if len(themes) > 0:
            print(f"First theme: {json.dumps(themes[0], ensure_ascii=False, indent=2)}")
            # 检查必要字段
            first_theme = themes[0]
            print(f"Has style_id: {'style_id' in first_theme}")
            print(f"Has tpl_id: {'tpl_id' in first_theme}")
            print(f"Has style_name_list: {'style_name_list' in first_theme}")
else:
    print(f"Error in response: {result}")

# 测试生成大纲
print("\n=== Testing outline generation ===")
outline_url = "https://qianfan.baidubce.com/v2/tools/ai_ppt/generate_outline"
outline_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
}
outline_data = {
    "query": "2025年经济报告PPT"
}

try:
    response = requests.post(outline_url, headers=outline_headers, json=outline_data, stream=True, timeout=30)
    print(f"Outline Status Code: {response.status_code}")
    
    # 读取流式响应
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data:'):
                data_str = line_str[5:].strip()
                print(f"Received data: {data_str[:100]}...")
                try:
                    data_obj = json.loads(data_str)
                    print(f"Parsed keys: {list(data_obj.keys())}")
                except:
                    pass
                break  # 只看第一条
    
except Exception as e:
    print(f"Outline error: {e}")
    import traceback
    traceback.print_exc()
