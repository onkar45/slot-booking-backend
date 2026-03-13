import requests

BASE_URL = "http://127.0.0.1:8000"

def test_super_admin_flow():
    # 1. Login
    print("Logging in...")
    login_data = {
        "email": "superadmin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("Login failed:", response.json())
        return

    data = response.json()
    token = data.get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful. Role:", data.get("role"))

    # 2. Get Dashboard Stats
    print("\nFetching Dashboard Stats...")
    res = requests.get(f"{BASE_URL}/super-admin/dashboard", headers=headers)
    print(res.status_code, res.json())

    # 3. Get Company Analytics
    print("\nFetching Company Analytics...")
    res = requests.get(f"{BASE_URL}/super-admin/company-analytics", headers=headers)
    print(res.status_code, res.json())

    # 4. Get User Bookings
    print("\nFetching User Bookings...")
    res = requests.get(f"{BASE_URL}/super-admin/user-bookings", headers=headers)
    print(res.status_code, f"Returned {len(res.json())} bookings")

    # 5. Check Login Activity
    print("\nFetching Login Activity...")
    res = requests.get(f"{BASE_URL}/super-admin/login-activity", headers=headers)
    print(res.status_code, f"Returned {len(res.json())} login records")
    if res.status_code == 200 and len(res.json()) > 0:
        print("Latest login IP:", res.json()[0].get("ip_address"))

if __name__ == "__main__":
    test_super_admin_flow()
