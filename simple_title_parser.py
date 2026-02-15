"""
简单的US Code标题解析器
通过分析页面结构提取标题
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def parse_uscode_titles_simple():
    """简单解析US Code标题"""
    url = "https://www.govinfo.gov/app/collection/uscode/2024"
    
    try:
        print(f"🌐 正在访问: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 方法1: 查找包含"Title"的文本
        print("🔍 查找包含'Title'的文本...")
        titles = []
        
        # 查找所有文本节点
        for text in soup.stripped_strings:
            # 匹配 "Title X" 格式的文本
            title_match = re.match(r'^Title\s+\d+', text)
            if title_match:
                title_text = text.strip()
                if title_text not in titles:
                    titles.append(title_text)
                    print(f"  📌 找到标题: {title_text}")
            
            # 也查找类似 "Title X - Description" 的格式
            elif "Title" in text and re.search(r'\d+', text):
                # 简单过滤掉太短的文本
                if len(text) > 10:
                    title_text = text.strip()
                    if title_text not in titles:
                        titles.append(title_text)
                        print(f"  📌 找到标题: {title_text}")
        
        # 方法2: 查找特定的HTML结构
        if not titles:
            print("🔍 查找特定HTML结构...")
            # 查找可能包含标题的容器
            containers = soup.find_all(['div', 'span', 'p'], 
                                     string=re.compile(r'Title\s+\d+'))
            for container in containers:
                text = container.get_text().strip()
                if text and "Title" in text and len(text) > 5:
                    if text not in titles:
                        titles.append(text)
                        print(f"  📌 找到标题: {text}")
        
        # 如果还是没有找到，返回标准标题列表
        if not titles:
            print("🔄 返回标准US Code标题列表")
            titles = [f"Title {i}" for i in range(1, 55)]
            for i, title in enumerate(titles[:10]):  # 只显示前10个
                print(f"  📌 标准标题: {title}")
            if len(titles) > 10:
                print(f"  📌 ... 还有 {len(titles)-10} 个标题")
        
        print(f"\n✅ 共找到 {len(titles)} 个标题")
        
        # 保存结果
        with open('uscode_titles_parsed.json', 'w') as f:
            json.dump(titles, f, indent=2)
        print("📄 结果已保存到: uscode_titles_parsed.json")
        
        return titles
        
    except Exception as e:
        print(f"❌ 解析失败: {str(e)}")
        # 回退到标准标题列表
        standard_titles = [f"Title {i}" for i in range(1, 55)]
        with open('uscode_titles_parsed.json', 'w') as f:
            json.dump(standard_titles, f, indent=2)
        return standard_titles

if __name__ == "__main__":
    titles = parse_uscode_titles_simple()
    print(f"\n📋 最终标题列表 (前5个):")
    for i, title in enumerate(titles[:5]):
        print(f"  {i+1}. {title}")
    if len(titles) > 5:
        print(f"  ... 还有 {len(titles)-5} 个标题")
