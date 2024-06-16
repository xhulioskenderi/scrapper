from fastapi import FastAPI, HTTPException, Depends
import sys
sys.path.append("..")
from proxy_rotator import ScoreBasedProxyRotator
from starlette.requests import Request
import os
from selenium_instance_caching import CustomCache

app = FastAPI()
proxy_rotator = ScoreBasedProxyRotator()
#The capacity of how many proxies can be saved in the cache to be used in concurrent sessions
cache = CustomCache(capacity=10000)

API_KEY = os.environ.get('FLASK_API_KEY')
print(API_KEY)
if not API_KEY:
    raise ValueError("No API key set in the environment!")


# Dependency to verify the API key in the header
def verify_api_key(request: Request):
    api_key = request.headers.get("Authorization")
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/get_proxy/{instance_id}")
async def get_proxy(instance_id: str, api_key: str = Depends(verify_api_key)):
    proxy_info = cache.get(instance_id)
    if proxy_info is None:
        if cache.is_full():
            raise HTTPException(status_code=429, detail='Cache is at capcity')
        # Get a new proxy if there's none in the cache
        proxy_info = proxy_rotator.get_proxy()
        cache.put(instance_id, proxy_info)
    return proxy_info

@app.post("/remove_proxy/{instance_id}")
async def remove_proxy(instance_id: str = Depends(verify_api_key)):
    try:
        cache.delete(instance_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="No such proxy in cache")
    

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)