import os
import sys
import requests
import json
import argparse

URL_PREFIX = "https://qianfan.baidubce.com/v2/tools/ai_ppt/"


def get_ppt_theme(api_key: str):
    headers = {
        "Authorization": "Bearer %s" % api_key,
    }
    response = requests.post(URL_PREFIX + "get_ppt_theme", headers=headers)
    result = response.json()
    if "errno" in result and result["errno"] != 0:
        raise RuntimeError(result["errmsg"])
    
    themes = result["data"]["ppt_themes"]
    if not themes:
        raise RuntimeError("No themes available")
    
    # 使用第一个主题
    first_theme = themes[0]
    return {
        "style_id": first_theme["style_id"],
        "tpl_id": first_theme["tpl_id"],
        "style_name_list": first_theme["style_name_list"]
    }


def ppt_outline_generate(api_key: str, query: str):
    headers = {
        "Authorization": "Bearer %s" % api_key,
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    
    params = {
        "query": query,
    }
    
    title = ""
    outline = ""
    chat_id = ""
    query_id = ""
    
    response = requests.post(URL_PREFIX + "generate_outline", 
                            headers=headers, 
                            json=params, 
                            stream=True,
                            timeout=60)
    
    if response.status_code != 200:
        print(f"Outline request failed: {response.status_code}")
        print(response.text)
        return {"chat_id": "", "query_id": "", "title": "", "outline": ""}
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data:'):
                data_str = line_str[5:].strip()
                try:
                    delta = json.loads(data_str)
                    if "title" in delta and delta["title"]:
                        title = delta["title"]
                    if "chat_id" in delta and delta["chat_id"]:
                        chat_id = delta["chat_id"]
                    if "query_id" in delta and delta["query_id"]:
                        query_id = delta["query_id"]
                    if "outline" in delta:
                        outline += delta["outline"]
                    if delta.get("is_end", False):
                        break
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    continue
    
    return {
        "chat_id": chat_id,
        "query_id": query_id,
        "title": title,
        "outline": outline
    }


def ppt_generate(api_key: str, query: str, web_content: str = None):
    print(f"开始生成PPT: {query}")
    
    # 1. 获取主题
    print("获取PPT主题...")
    try:
        theme = get_ppt_theme(api_key)
        print(f"使用主题: {theme['style_name_list']}")
    except Exception as e:
        print(f"获取主题失败: {e}")
        return
    
    # 2. 生成大纲
    print("生成PPT大纲...")
    outline_data = ppt_outline_generate(api_key, query)
    
    if not outline_data["outline"]:
        print("大纲生成失败或为空")
        return
    
    print(f"大纲标题: {outline_data['title']}")
    print(f"大纲内容预览: {outline_data['outline'][:200]}...")
    
    # 3. 生成PPT
    print("生成PPT文件...")
    headers = {
        "Authorization": "Bearer %s" % api_key,
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    
    params = {
        "query_id": int(outline_data["query_id"]) if outline_data["query_id"] else 0,
        "chat_id": int(outline_data["chat_id"]) if outline_data["chat_id"] else 0,
        "query": query,
        "outline": outline_data["outline"],
        "title": outline_data["title"],
        "style_id": theme["style_id"],
        "tpl_id": theme["tpl_id"],
        "web_content": web_content
    }
    
    print(f"生成参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(URL_PREFIX + "generate_ppt_by_outline", 
                                headers=headers, 
                                json=params, 
                                stream=True,
                                timeout=120)
        
        if response.status_code != 200:
            print(f"PPT生成请求失败: {response.status_code}")
            print(response.text)
            return
        
        final_result = None
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data:'):
                    data_str = line_str[5:].strip()
                    try:
                        result = json.loads(data_str)
                        print(f"进度: {result.get('status', 'unknown')}")
                        
                        if result.get("is_end", False):
                            final_result = result
                            break
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {e}")
                        continue
        
        if final_result:
            print("\n=== PPT生成完成 ===")
            print(json.dumps(final_result, ensure_ascii=False, indent=2))
            
            # 检查是否有下载链接
            if "data" in final_result and "download_url" in final_result["data"]:
                print(f"\nPPT下载链接: {final_result['data']['download_url']}")
            elif "download_url" in final_result:
                print(f"\nPPT下载链接: {final_result['download_url']}")
            else:
                print("\n未找到下载链接，完整响应:")
                print(json.dumps(final_result, ensure_ascii=False, indent=2))
        else:
            print("PPT生成未完成或未返回最终结果")
            
    except Exception as e:
        print(f"PPT生成过程错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成PPT")
    parser.add_argument("--query", "-q", type=str, required=True, help="PPT主题")
    parser.add_argument("--web_content", "-wc", type=str, default=None, help="网页内容")
    args = parser.parse_args()
    
    api_key = os.getenv("BAIDU_API_KEY")
    if not api_key:
        print("错误: 需要设置 BAIDU_API_KEY 环境变量")
        sys.exit(1)
    
    print(f"主题: {args.query}")
    ppt_generate(api_key, args.query, args.web_content)
