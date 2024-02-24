import requests
import time



def get_user_ids(page_size=50):
    base_url = "http://local.adspower.net:50325/api/v1/user/list"
    params = {
        "page_size": page_size
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["code"] == 0:
            user_list = data["data"]["list"]
            profile_ids = [user["user_id"] for user in user_list]
            return profile_ids
        else:
            print("API 请求失败。错误信息：", data["msg"])
            return []
    except requests.RequestException as e:
        print("API 请求失败：", e)
        return []



def check_account_status(user_id):
    base_url = "http://local.adspower.net:50325/api/v1/browser/active"
    params = {
        "user_id": user_id
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["code"] == 0:
            status = data["data"]["status"]
            return status
        else:
            print("检查账号状态失败。错误信息：", data["msg"])
            return None
    except requests.RequestException as e:
        print("API 请求失败：", e)
        return None

def close_account_browser(user_id):
    base_url = "http://local.adspower.net:50325/api/v1/browser/stop"
    params = {
        "user_id": user_id
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["code"] == 0:
            print("已关闭账号浏览器。")
        else:
            print("关闭账号浏览器失败。错误信息：", data["msg"])
    except requests.RequestException as e:
        print("API 请求失败：", e)

def delete_user_accounts(user_ids):
    base_url = "http://local.adspower.net:50325/api/v1/user/delete"
    batch_size = 100  # 一次删除的最大用户数量

    for i in range(0, len(user_ids), batch_size):
        batch_user_ids = user_ids[i:i + batch_size]
        payload = {
            "user_ids": batch_user_ids
        }

        try:
            response = requests.post(base_url, json=payload)
            data = response.json()

            if data["code"] == 0:
                print(f"已删除 {len(batch_user_ids)} 个账号。")
            else:
                print("API 请求失败。错误信息：", data["msg"])
        except requests.RequestException as e:
            print("API 请求失败：", e)

        time.sleep(1)
