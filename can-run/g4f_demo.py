from g4f.client import Client
import time


for i in range(50):
    print(f"第{i+1}次测试")
    t1 = time.time()
    client = Client()
    t2 = time.time()
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": "Hello"}],
        web_search=False
    )
    t3 = time.time()
    print(f"耗时情况: {t2-t1:.2f}秒(初始化), {t3-t2:.2f}秒(请求), 回复\n{response.choices[0].message.content}")


# client = Client()
# response = client.images.generate(
#     model="flux",
#     prompt="a white siamese cat",
#     response_format="url"
# )

# print(f"Generated image URL: {response.data[0].url}")

# t1=time.time()
# client = Client()
# t2=time.time()
# response = client.chat.completions.create(
#     model="gpt-4.1",
#     messages=[{"role": "user", "content": "Hello"}],
#     web_search=False
# )
# t3=time.time()
# print(f"耗时情况: {t2-t1:.2f}秒(初始化), {t3-t2:.2f}秒(请求), 回复\n{response.choices[0].message.content}")