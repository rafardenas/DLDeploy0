import jwt

encoded_jwt = jwt.encode({"some": "payload"}, "secret", algorithm="HS256")
print(encoded_jwt)


token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJyZXNldF9wYXNzd29yZCI6MywiZXhwIjoxNjI2MjY2OTY2LjA4MzgwOTF9.WqTWctNt0nab8lQ1cbxcnjUoRWDnpuZ5_cM0sfO-JaY"
id = jwt.decode(token, "secret", algorithm="HS256")
print(id)
