import requests
import time
def test_through_load_balancer():
    proxies = {
        "http": "http://localhost:8112",
        "https": "http://localhost:8112",
    }

    response = requests.get("https://opm.openresty.org", proxies=proxies)
    print(f"Received: {response.text}")
    time.sleep(1000)
if __name__ == "__main__":
    test_through_load_balancer()

