import pycurl
from io import BytesIO
from loguru import logger
from urllib.parse import urlencode


def send_http_request(port: int, method, params: dict = None, timeout=10):
    url = f"http://localhost:{port}/{method}"
    logger.debug(f"request:{url}")

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.TIMEOUT, timeout)
    if params:
        param_str = urlencode(params)
        logger.debug(f"request:{url}?{param_str}")

        c.setopt(c.URL, f"{url}?{param_str}")

    try:
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        response_code = c.getinfo(pycurl.HTTP_CODE)
        if response_code == 200:
            content_type = c.getinfo(pycurl.CONTENT_TYPE)
            buffer.seek(0)
            response_content = buffer.read()
            if 'image/jpeg' in content_type or 'image/png' in content_type:
                logger.debug(f"Request successful, response content: Image content:{response_content[:100]}")
                return response_content
            else:
                response_text = response_content.decode('utf-8')
                logger.debug(f"response:{response_text[:100]}")
                if "<?xml version='1.0' " in response_text:
                    logger.debug(f"response:{response_text[-15:]}")
                return response_text
        else:
            logger.error(f"Request failed, status code: {response_code}")
    except pycurl.error as e:
        logger.error(f"An error occurred during the request: {e}")
    finally:
        c.close()
        buffer.close()