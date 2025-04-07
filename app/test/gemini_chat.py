from PIL import Image
from google import genai

client = genai.Client(api_key="AIzaSyDmjcf_ZssOrf0BM58QeHc1VxGasaZe5Fo")

image = Image.open("/home/nnikolovskii/PycharmProjects/dina/assets/snickerts.jpg")
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[image, "extract the ingredients."]
)
print(response.text)
