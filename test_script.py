import time
import requests

BASE_URL = "http://127.0.0.1:8000"  # We'll use localhost

def run_tests():
    print("--- Starting Verification ---")
    
    # 1. Login/Signup via OAuth
    print("Test 1: Authenticate")
    auth_payload = {
        "email": "test@example.com",
        "username": "test_user",
        "provider_id": "google_12345"
    }
    res = requests.post(f"{BASE_URL}/users/oauth", json=auth_payload)
    if res.status_code != 200:
        print("Auth failed:", res.text)
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Auth Success.")
    
    # 2. Get Market Quote
    print("Test 2: Quote")
    res = requests.get(f"{BASE_URL}/market/quote/RELIANCE.NS", headers=headers)
    if res.status_code != 200:
        print("Quote failed:", res.text)
    else:
        print("Quote success:", res.json())
        
    # 3. Buy a Stock
    print("Test 3: Buy Stock")
    buy_payload = {"ticker_symbol": "RELIANCE.NS", "quantity": 10}
    res = requests.post(f"{BASE_URL}/trade/buy", json=buy_payload, headers=headers)
    if res.status_code != 201:
        print("Buy failed:", res.text)
    else:
        print("Buy success:", res.json())
        
    # 4. Sell a Stock
    print("Test 4: Sell Stock")
    sell_payload = {"ticker_symbol": "RELIANCE.NS", "quantity": 5}
    res = requests.post(f"{BASE_URL}/trade/sell", json=sell_payload, headers=headers)
    if res.status_code != 201:
        print("Sell failed:", res.text)
    else:
        print("Sell success:", res.json())
        
    # 5. Get Portfolio
    print("Test 5: Portfolio")
    res = requests.get(f"{BASE_URL}/portfolio", headers=headers)
    if res.status_code != 200:
        print("Portfolio failed:", res.text)
    else:
        print("Portfolio success:", res.json())

if __name__ == "__main__":
    run_tests()
