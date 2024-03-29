import requests
import json, re
from bs4 import BeautifulSoup

def trading_analysis(chart_url:str):
    url = f'https://charteye.ai/api/status?url=https://www.tradingview.com/x/{chart_url}/'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # If successful, print the response data
        data = response.text
        response_text = data.split("data:")
        result = []
        for i in response_text:
            if i:
                result.append(json.loads(i))
        return result
    else:
        # If not successful, print an error message
        return False

def ta_response(chart_url:str):
    ta = trading_analysis(chart_url=chart_url)
    main_analysis = False
    if ta == False:
        return False
    else:
        for i in ta:
            try:
                if "Successfully generated analysis" in i["title"]:
                    main_analysis = i["description"]
                    break
                else:
                    pass
            except:
                pass
    if main_analysis == False:
        return main_analysis
    else:
        return convert_html_for_telegram(main_analysis).replace("\n", "", 1)

def convert_html_for_telegram(html_content):
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(html_content, features="html.parser")
  
    # Convert header tags to bold text
    for header in soup.find_all(['h2']):
        header.replace_with(f"\n<b>{header.text}</b>\n")
    for header in soup.find_all(['h3']):
        header.replace_with(f"\n<b>{header.text}</b>\n")
    # Convert lists into plain text with dashes for bullet points
    for ul in soup.find_all('ul'):
        new_ul = []
        for li in ul.find_all('li'):
            # print(li.find_all('a'))
            # li_text = f'{li.text}'
            if li.find_all('a') == []:
                new_ul.append(f"- {li.text}")
            else:
                lk = ''
                for i in li.contents:
                    lk = lk + f'{i}' + " "
                new_ul.append(f"- {lk.strip()}")
        ul.replace_with('\n'.join(new_ul))
    
    # Convert emphasis tags to italic text
    for em in soup.find_all('em'):
        em.replace_with(f"<em>{em.text}</em>")
    
    # Convert anchor tags keeping the hyperlinks
    for a in soup.find_all('a'):
        a.replace_with(f'<a href="{a.get("href")}">{a.text}</a>')
      
    # Convert strong tags to bold text
    for strong in soup.find_all('strong'):
        strong.replace_with(f"<b>{strong.text}</b>")
    
    return soup.get_text(separator='')
