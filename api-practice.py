import requests

response = requests.get('https://jsonplaceholder.typicode.com/users/2')

print(f"Status code: {response.status_code}")
print(f"Content type: {response.headers.get('content-type')}")
print("---")
print("Raw text response: ")
print(response.text)


print("----------")
print("parsed as JSON")
user=response.json()
print(f"Name:{user['name']}")
print(f"Email:{user['email']}")
print(f"Company:{user['company']['name']}")
print(f"City: {user['address']['city']}")

print("----")

print("Now making a POST request....")

new_post = {
    'title': 'My day 3 of AI Engineering',
    'body': 'Today I learned what an API is and made my first calls',
    'userId': 1
}

post_response = requests.post(
    'https://jsonplaceholder.typicode.com/posts',
    json=new_post
)

print(f"Stauts code: {post_response.status_code}")
print(f"Server response:")
print(post_response.json())

print("---")

print("Get request with custom headers:")

headers = {
    'User-Agent': 'TaimoorBot/1.0',
    'Accept': 'application/json'
}

response = requests.get('https://jsonplaceholder.typicode.com/users/1', headers= headers
)

print(f"Status: {response.status_code}")
print(f"Got user: {response.json()['name']}")

print("---")
print("Error handling demo")

def fetch_user(user_id):
    try:
        response = requests.get(
            f'https://jsonplaceholder.typicode.com/users/{user_id}',
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for user {user_id}: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"Timeout for user {user_id}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Could not connect (internet down?)")
        return None

for uid in [1,9999]:
    result= fetch_user(uid)
    if result:
        print(f"Got:{result}['name']")
    else:
        print(f"No data for {uid}")