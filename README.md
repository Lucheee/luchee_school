# Student Management System

Note: This is currently under active development

## Table of Contents

- [Student Management System](#student-management-system)
  - [Table of Contents](#table-of-contents)
  - [Live ( deployed version )](#live--deployed-version-)
  - [Testing Locally](#testing-locally)
  - [Available Endpoint](#available-endpoint)
    - [Auth Endpoint](#auth-endpoint)
    - [Students Endpoint](#students-endpoint)
    - [Courses Endpoint](#courses-endpoint)
    - [Grades Endpoint](#grades-endpoint)

## Live ( deployed version ) 

Visit [website](http://olakaycoder1.pythonanywhere.com/)
## Testing Locally

Clone the repository

```console
git clone https://github.com/Lucheee/luchee_school.git
```

Change directory to the cloned folder

```console
cd luchee_school
```

Install necessary dependency to run the project

```console
pip install -r requirements.txt
```
Create database from migration files 

```console
flask db migrate -m "your description"
```

```console
flask db upgrade
```
Run application

```console
flask run
```


The action perform will create an admin user and a student with the following credentials

| USER TYPE | FULL NAME | EMAIL | PASSWORD |
| ------- | ----- | ------|------- | ----- |
| __Admin__ | AdminOne | admin1@gmail.com | _password123_ |
| __Student__ | StudentTwo | student2@gmail.com | _password123_ |

also with two courses `Mathematics` and `Geography`

The student created will then be register to Mathematics course.

Continue testing......



## Available Endpoint

### Auth Endpoint
| ROUTE | METHOD | DESCRIPTION | AUTHORIZATION  | USER TYPE |  PLACEHOLDER | 
| ------- | ----- | ------------ | ------|------- | ----- |
|  `auth/register/student` | _POST_ | It allows the  creation of a student account   | Any | Any |  ---- | 
|  `auth/register/admin` |  _POST_ | It allows the creation of an admin account   | Authenticated | Admin | ---- | 
|  `auth/login` |  _POST_  | It allows user authentication   | Any | Any | ---- | 
|  `auth/refresh` |  _POST_  | It allows user refresh their tokens   | Authenticated | Any | ---- | 

### Students Endpoint
| ROUTE | METHOD | DESCRIPTION | AUTHORIZATION  | USER TYPE |  PLACEHOLDER | 
| ------- | ----- | ------------ | ------|------- | ----- |
|  `students/all_students` |  _GET_  | It allows the retrieval all student is the school   | Authenticated | Admin | ---- |
|  `students/<student_id>` |  _GET_  | It allows the  retrieval of a student | Authenticated | Admin | A student ID |
|  `students/delete/<student_id>` |  _DELETE_  | It allows the  deleting a student | Authenticated | Admin | A student ID |
|  `students/update` |  _PUT_  | It allows the  updating of a student | Authenticated | Admin | A student ID |


### Courses Endpoint
| ROUTE | METHOD | DESCRIPTION | AUTHORIZATION  | USER TYPE |  PLACEHOLDER | 
| ------- | ----- | ------------ | ------|------- | ----- |
|  `courses/all-courses` |  _GET_  | It allows the retrieval of all available courses   | Authenticated | Admin | ---- |
|  `courses/create_course` |  _POST_  | It allows the creation of a new course   | Authenticated | Admin | ---- |
|  `courses/<course_id>` |  _DELETE_  | It allows deleting a course   | Authenticated | Admin | ---- |
|  `courses/<course_id>/students` |  _GET_  | It allows the  retrieval of all students in a courses | Authenticated | Admin  | A course ID |
|  `courses/<student_id>/courses` |  _GET_  | It allows the retrieval of a student courses   | Authenticated | Admin | A student ID |
|  `courses/<course_id>/register` |  _POST_  | It allows student register a course   | Authenticated | Any | ---- |
|  `courses/delete-reg-student/<course_id>/<student_id>` |  _DELETE_  | It allows student unregister a course   | Authenticated | Admin | ---- |



### Grades Endpoint
| ROUTE | METHOD | DESCRIPTION | AUTHORIZATION  | USER TYPE |  PLACEHOLDER | 
| ------- | ----- | ------------ | ------|------- | ----- |
|  `grades/<student_id>/grades` |  _GET_  | It allows the retrieval a student all courses grade   | Authenticated | Admin | A student ID |
|  `grades/<student_id>/gpa` |  _GET_  | Calculate a student gpa score   | Authenticated | Admin | A student ID |
|  `grades/course/add_score` |  _PUT_  | It allow admin add a student score in a course | Authenticated | Admin | ---- |




