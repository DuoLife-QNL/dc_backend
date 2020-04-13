# 项目说明
2017级大创项目——“基于机器学习的手写体字符识别系统”

## 初始化数据库

```bash
flask init-db
```

# 接口说明
* 接口接收与返回数据均为`json`格式
* **用户身份认证采用JWT方式**
  * Token 认证方式（前端发送http请求时在Headers中添加的字段）：key = `Authorization` value = `Bearer {{Token}}`
  * 对于所有标注了`jwt required`的接口，当发生Token错误时：
    * 若Token未注册，返回：`"msg": "Signature verification failed"`
    * 若Token已过期，返回：`"msg": "Token has expired"`

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

## /paper
**JWT required**
### /paper/upload/image
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

### /paper/upload/answer
* 作用：上传用户在前端手动确认或修改后的最终识别答案
* 注意：每次上传答案，若该试卷已存在，试卷答案会被全部替换，而不管答案数目如何
* method: post
* content
  *  examID
  *  book：第几本
  *  page：第几张
  *  answer：一个list，每一项为一道题的答案，若考生未作答，传"X"

## /exam
/exam 下所有的接口均为jwt required
### /exam/create

* 作用：用户创建考试
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

### /exam/modify
* 作用：用户修改考试信息
* method = post
* content
  * id: exam id, 必须传输此项
  * name: 修改之后的考试名称，若不传输，则不修改考试名称，下同
  * description
  * std_answer：一个list，list中的每一项是一个dict，用于指明修改哪道题，包含三个字段：
    * problem_no：题号
    * problem_score：分值
    * content：修改后的答案
* example
```json
{
	"id" : 100005,
	"name" : "Modified name",
	"description" : "modify test",
	"std_answer" : [
		{
			"problem_no" : 2,
			"problem_score" : 3,
			"content" : "C"
		},
		{
			"problem_no" : 4,
			"problem_score" : 1,
			"content" : "D"
		}
	]
}
```
* return value
  * result = "Succeeded"

### exam/get-exam-info
* 作用：通过考试id获取考试信息
* method = post
* content
  * id: exam id
* return value
  * id
  * name
  * description
  * std_answer: 一个list，按照题号顺序排列（此处不考虑选择题题号不连续的情况），其中每一项由答案和分值组成，如`A2`表示此题答案为A，占2分
* return example
```json
{
  "description": "Modified name",
  "id": 100005,
  "name": "Modified name",
  "std_answer": [
    "A2",
    "B3",
    "C3",
    "D1"
  ]
}
```
其中，`B3`表示第二题答案为B，占三分。

### exam/get-user-exam
* method = get
* content: no need to send http body
* return value:
  * exam_info: 一个list，其中每一项为一个dict，并包含三个字段：
    * id
    * name
    * description
* return example:
```json
{
  "exam_info": [
    {
      "description": "测试接口, test api",
      "id": 100003,
      "name": "测试test3"
    },
    {
      "description": "测试接口, test api",
      "id": 100004,
      "name": "测试test4"
    },
    {
      "description": "Modified name",
      "id": 100005,
      "name": "Modified name"
    }
  ]
}
```

### exam/delete
* 作用：删除考试，**注意，这会导致级联删除考试的所有信息**
* method = post
* content
  * examID

### exam/get-book-answer
* 以本为单位获取考生答题情况
* method = post
* content
  * examID
  * book
* return example:
```json
{
  "1": [
    "D",
    "A",
    "B",
    "D"
  ],
  "2": [
    "C",
    "B",
    "A",
    "D"
  ],
  "3": [
    "D",
    "C",
    "B",
    "D"
  ],
  "4": [
    "D",
    "C",
    "B",
    "A"
  ]
}
```
其中，1、2、3、4代表第几章卷子，每张卷子的四道题答案在随后的list中按顺序列出

### exam/get-total-answer
* 获取一场考试考生的整体答题情况
* 返回信息：每道题选择A、B、C、D的人数
* method = post
* content
  * examID
* return example
```json
{
  "1": {
    "C": 2,
    "D": 4
  },
  "2": {
    "A": 1,
    "B": 1,
    "C": 4
  },
  "3": {
    "A": 1,
    "B": 5
  },
  "4": {
    "A": 1,
    "D": 5
  }
}
```
其中，最外侧的数字代表题号，每个题号之后的dict中表示本题选项的选择人数。若无某个选项，表示选择人数为0。特别地，O代表未作答，X代表其它非常规选项。