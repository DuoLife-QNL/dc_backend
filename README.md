# 项目说明
2017级大创项目——“基于机器学习的手写体字符识别系统”

## 初始化数据库

```bash
flask init-db
```

## 接口说明
接口接收与返回数据均为`json`格式

### /auth/register

#### mothod = post
#### content
```json
{
    "username": "username",
    "password": "password"
}
```
#### return value
If succeessfully registered the user, return:
```json
{
    "result": "Succeeded"
}
```
Otherwise, return:
```json
{
    "result": "Failed",
    "message": "User {{username}} has already been registered"
}
```

### /auth/login

#### mothod = post
#### content
```json
{
    "username": "username",
    "password": "password"
}
```
#### return value
If successfully logged in, return:
```json
{
    "result": "Succeeded",
    "access_token": "{{Token}}"
}
```
Otherwise, return:
```json
{
    "result": "Failed",
    "message": "Bad username or password"
}
```

### /upload/img
JWT required
#### method = post
#### content
```json
{
    "imageData": "{{base64_img_str}}",
    "bookNo": "{{book_number}}",
    "paperNo": "{{paper_number}}"
}
```
#### return value
* `valid`: 若识别到了与预期题目数相同的题目数，则返回`True`， 否则返回 `False`
* `letters`: 一个list，其中的每一项代表识别到的一个字母，每一项由以下四个参数描述：
    * no: the number of the letter
    * class: which letter it is
    * box: the location of the letter
    * score: accurate score of recognition
    
返回值为由`valid`和`letters`组成的json