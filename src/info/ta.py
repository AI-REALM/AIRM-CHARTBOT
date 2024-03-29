import requests
import json

def trading_analysis(chart_url:str):
    url = f'https://charteye.ai/api/status?url=https://www.tradingview.com/x/{chart_url}/'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # If successful, print the response data
        print(response.text)

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
            if "Successfully generated analysis" in i["title"]:
                main_analysis = i["description"]
                break
            else:
                pass
    return main_analysis

print(ta_response("x5UmRXm8"))