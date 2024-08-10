import resuests
import re


def readAPI_fetch_content(url):
    api_key = None

    def fetch(url, headers):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type'):
            return response.json()
        else:
            raise requests.exceptions.ContentTypeError(
                f"Unexpected content type: {response.headers.get('Content-Type')}"
            )

    def remove_unwanted_text(text):
        url_pattern = re.compile(r'\(https?://[^\)]+\)')
        mailto_pattern = re.compile(r'\(mailto:[^\)]+\)')
        brackets_pattern = re.compile(r'\[.*?\]')
        text = url_pattern.sub('', text)
        text = mailto_pattern.sub('', text)
        text = brackets_pattern.sub('', text)
        text = '\n'.join([line for line in text.split('\n') if line.strip()])
        return text

    headers_common = {
        "Accept": "application/json",
    }

    if api_key:
        headers_common["Authorization"] = f"Bearer {api_key}"

    url1 = f"https://r.jina.ai/{url}"
    retries = 3
    delay = 60  # seconds

    result = {
        'success': False,
        'error': f"Failed to fetch {url} after {retries} attempts"
    }

    for attempt in range(retries):
        logging.info(f"readerAPI Process {url}, attempt {attempt + 1}")
        try:
            response_default = fetch(url1, headers_common)
            default_content = response_default.get('data').get('content')
            clean_default_content = remove_unwanted_text(default_content)

            result = {
                'success': True,
                'content': clean_default_content,
            }
            break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logging.warning(f"429 Too Many Requests for url: {url}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                result = {
                    'success': False,
                    'error': f"Error fetching {url}: {str(e)}"
                }
                break
        except Exception as e:
            result = {
                'success': False,
                'error': f"Error fetching {url}: {str(e)}"
            }
            break

    return result

url = "https://www.snopes.com/fact-check/simone-biles-falling-competition/"

result = readAPI_fetch_content(url)
print(result)
