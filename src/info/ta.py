import requests
import json, re
import base64
from bs4 import BeautifulSoup


def convert_html_for_telegram(html_content):
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(html_content, features="html.parser")
  
    # Convert header tags to bold text
    for header in soup.find_all(["h2"]):
        header.replace_with(f"\n<b>{header.text}</b>\n")
    for header in soup.find_all(["h3"]):
        header.replace_with(f"\n<b>{header.text}</b>\n")
    # Convert lists into plain text with dashes for bullet points
    for ul in soup.find_all("ul"):
        new_ul = []
        for li in ul.find_all("li"):
            # print(li.find_all("a"))
            # li_text = f"{li.text}"
            if li.find_all("a") == []:
                new_ul.append(f"- {li.text}")
            else:
                lk = ""
                for i in li.contents:
                    lk = lk + f"{i}" + " "
                new_ul.append(f"- {lk.strip()}")
        ul.replace_with("\n".join(new_ul))
    
    # Convert emphasis tags to italic text
    for em in soup.find_all("em"):
        em.replace_with(f"<em>{em.text}</em>")
    
    # Convert anchor tags keeping the hyperlinks
    for a in soup.find_all("a"):
        a.replace_with(f'<a href="{a.get("href")}">{a.text}</a>')
      
    # Convert strong tags to bold text
    for strong in soup.find_all("strong"):
        strong.replace_with(f"<b>{strong.text}</b>")
    
    return soup.get_text(separator="")

def get_image_as_base64_with_url(image_url):

    # # Replace "YOUR_IMAGE_URL_HERE" with your PNG image URL
    # image_url = "https://api.telegram.org/file/bot7144158465:AAFzpfFgORQ2veBlq_TNWA7yZBznwLAgHc4/photos/file_5.jpg"
    # Make an HTTP GET request to fetch the image
    response = requests.get(image_url)

    # Ensure the request was successful
    if response.status_code == 200:
        # Convert the image bytes to a Base64 string
        image_base64 = base64.b64encode(response.content)

        # Optional: Convert Base64 bytes to string for easier use/display
        image_base64_str = image_base64.decode("utf-8")

        # Output or use the Base64 string
        return image_base64_str
    else:
        return False
    
def get_technical_analysis(image_base64_str):
    url = "https://api.chartai.tech/charteye/analyze/stream"
    payload = {
        "locale": "en",
        "url": f"data:image/jpeg;base64,{image_base64_str}",
        "platform": "chrome"
    }
    headers = {
        "Authorization": "Bearer 0a62b766-8aad-4b84-aa89-8d0877bfb5a1",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response_data = response.text
            return response_data
        else:
            # Print the whole response if the status code is not 200
            print("Received non-JSON error response:", response.text)
            return False
    except requests.exceptions.RequestException as e:
        print(e)
        return False

def ta_response(image_url):
    image_base64_data = get_image_as_base64_with_url(image_url=image_url)
    if not image_base64_data:
        return False
    ta_html = get_technical_analysis(image_base64_str=image_base64_data)
    if not ta_html:
        return False
    
    ta_telegram = convert_html_for_telegram(html_content=ta_html)

    return ta_telegram