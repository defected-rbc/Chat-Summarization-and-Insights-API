import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Replace with actual IDs from your database
TEST_CONVERSATION_ID = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
TEST_USER_ID = "user_123"

# 1. Test Store Chat Messages (POST /api/chats)
def test_store_chat_message():
    endpoint = f"{BASE_URL}/chats"
    headers = {"Content-Type": "application/json"}
    payload = {
        "conversation_id": TEST_CONVERSATION_ID,
        "user_id": TEST_USER_ID,
        "sender_type": "user",
        "content": "This is a test message sent from Python.",
        "metadata": {"language": "en"}
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    print("Test Store Chat Messages:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response JSON: {response.json()}")
    print("-" * 30)

# 2. Test Retrieve Chats (GET /api/chats/{conversation_id})
def test_retrieve_chats():
    endpoint = f"{BASE_URL}/chats/{TEST_CONVERSATION_ID}"
    response = requests.get(endpoint)
    print("Test Retrieve Chats:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response JSON: {response.json()}")
    print("-" * 30)

# 3. Test Summarize Chat (POST /api/chats/summarize)
def test_summarize_chat():
    endpoint = f"{BASE_URL}/chats/summarize"
    headers = {"Content-Type": "application/json"}
    payload = {
        "conversation_id": TEST_CONVERSATION_ID
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    print("Test Summarize Chat:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response JSON: {response.json()}")
    print("-" * 30)

# 4. Test Get User's Chat History (GET /api/users/{user_id}/chats)
def test_get_user_chat_history():
    endpoint = f"http://127.0.0.1:8000/api/users/{TEST_USER_ID}/chats"
    params = {"page": 1, "limit": 5}
    response = requests.get(endpoint, params=params)
    print("Test Get User's Chat History (Page 1, Limit 5):")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response JSON: {response.json()}")
    print("-" * 30)

    params_page_2 = {"page": 2, "limit": 5}
    response_page_2 = requests.get(endpoint, params=params_page_2)
    print("Test Get User's Chat History (Page 2, Limit 5):")
    print(f"  Status Code: {response_page_2.status_code}")
    print(f"  Response JSON: {response_page_2.json()}")
    print("-" * 30)

# 5. Test Delete Chat (DELETE /api/chats/{conversation_id})
def test_delete_chat():
    endpoint = f"{BASE_URL}/chats/{TEST_CONVERSATION_ID}"
    response = requests.delete(endpoint)
    print("Test Delete Chat:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response JSON: {response.json()}")
    print("-" * 30)

# ... (previous test functions)

# 6. Test Generate Conversation Insights (POST /api/chats/{conversation_id}/insights)
def test_generate_conversation_insights():
    endpoint = f"{BASE_URL}/chats/{TEST_CONVERSATION_ID}/insights"
    response = requests.post(endpoint)
    print("Test Generate Conversation Insights:")
    print(f"  Status Code: {response.status_code}")
    print(f"  Response JSON: {response.json()}")
    print("-" * 30)

if __name__ == "__main__":
    # Replace with your actual conversation ID and user ID
    TEST_CONVERSATION_ID = "123"
    TEST_USER_ID = "user_123"


    print("Running API Tests:")
    test_store_chat_message()
    test_retrieve_chats()
    test_summarize_chat()
    test_get_user_chat_history()
    test_delete_chat()
    test_generate_conversation_insights() # Call the new test function