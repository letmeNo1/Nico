import pycurl
from io import BytesIO
from loguru import logger
from urllib.parse import urlencode

def send_http_request(port: int, method, params: dict = None, timeout=10):
    """
    Send an HTTP request to the specified endpoint and return the response.
    
    Args:
        port (int): Server port number
        method (str): API method name
        params (dict, optional): Query parameters. Defaults to None.
        timeout (int, optional): Request timeout in seconds. Defaults to 10.
    
    Returns:
        bytes or list or str: Response content based on Content-Type header
    """
    url = f"http://localhost:{port}/{method}"

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.TIMEOUT, timeout)
    
    if params:
        param_str = urlencode(params)
        c.setopt(c.URL, f"{url}?{param_str}")

    try:
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        response_code = c.getinfo(pycurl.HTTP_CODE)
        if response_code == 200:
            content_type = c.getinfo(pycurl.CONTENT_TYPE)
            buffer.seek(0)
            response_content = buffer.read()
            
            # Handle binary image responses
            if 'image/jpeg' in content_type or 'image/png' in content_type:
                return response_content
            
            # Handle JSON responses (including Base64-encoded image arrays)
            elif 'application/json' in content_type:
                try:
                    # Attempt standard JSON parsing
                    import json
                    response_json = json.loads(response_content.decode('utf-8'))
                    return response_json
                except json.JSONDecodeError:
                    # Handle non-standard JSON format (raw string array)
                    image_base64_list = response_content.decode('utf-8').strip('[]"').split('","')
                    return [b for b in image_base64_list if b]
            
            # Handle text-based responses
            else:
                response_text = response_content.decode('utf-8')
                return response_text
        else:
            buffer.seek(0)
            failure_preview = buffer.read(300).decode('utf-8', errors='replace')
            logger.error(
                f"Request failed with status code: {response_code}, url: {url}, params: {params}, "
                f"response preview: {failure_preview}"
            )
    except pycurl.error as e:
        logger.error(f"Request error: {e}, url: {url}, params: {params}")
    finally:
        c.close()
        buffer.close()