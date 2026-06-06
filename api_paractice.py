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