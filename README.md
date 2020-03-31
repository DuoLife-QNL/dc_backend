# 项目说明
2017级大创项目——“基于机器学习的手写体字符识别系统”

## 初始化数据库

```bash
flask init-db
```

# 接口说明
接口接收与返回数据均为`json`格式

## /auth/register

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

## /auth/login

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

## /upload/img
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

## /exam
### /exam/create

* method = post
* content
    * name: 考试名称
    * description: 对于考试的描述，可不传此字段
    * std_answer: 标准答案，格式为`["A2", "B2", "C3", "D1"]`，list中元素个数即为本次考试选择题数量，可根据实际情况传送答案数目。list中每个元素的第一个字段表示标准答案，第二个字段表示该题分数。如在上面示例中，第二个元素`B2`表示该场考试中第二题的标准答案为`B`，占2分。
* return value
  * If successfully created the exam, should return:
    * result: "Succeeded"
    * examID
  * The creation would fail if the exam already exists, in this case, backend should return:
    * result: "Failed"
    * message: "An exam of the same name already exists."