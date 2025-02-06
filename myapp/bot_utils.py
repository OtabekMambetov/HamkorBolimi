import requests

def add_product_to_django(name, description, price, image_path, token):
    url = "https://your-django-api-url/api/products/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "name": name,
        "description": description,
        "price": price,
    }
    files = {
        "image": open(image_path, "rb")
    }
    response = requests.post(url, headers=headers, data=data, files=files)
    return response.json()
