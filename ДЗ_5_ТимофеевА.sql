use oracle;

/* 1. Таблица Employees. Получить список всех сотрудников из 5го и из 8го отдела (department_id), которых наняли в 1998 году */

SELECT * FROM employees
WHERE
    YEAR(hire_date) = 1998 AND
    (department_id = 5 OR department_id = 8)
;

/* 2. Таблица Employees. Получить список всех сотрудников, у которых в имени содержатся минимум 2 буквы 'n' */

SELECT * FROM employees
WHERE first_name LIKE '%n%n%';

/* 3. Таблица Employees. Получить список всех сотрудников, у которых зарплата находится в промежутке от 8000 до 9000 (включительно) и/или кратна 1000 */

SELECT * FROM employees
WHERE
    MOD (salary, 1000) = 0 OR
    (salary BETWEEN 8000 AND 9000);

/* 4. Таблица Employees. Получить список всех сотрудников, у которых длина имени больше 10 букв и/или у которых в имени есть буква 'b' (без учета регистра) */

SELECT * FROM employees
WHERE
    CHAR_LENGTH(first_name) > 10 OR
    first_name LIKE '%b%'
;

/* 5. Таблица Employees. Получить первое 3х значное число телефонного номера сотрудника, если его номер в формате ХХХ.ХХХ.ХХХХ*/

SELECT *, SUBSTRING(phone_number, 1, 3) AS short_number
FROM employees
WHERE phone_number LIKE '___.___.____';

/* 6. Таблица Departments. Получить первое слово из имени департамента для тех, у кого в названии больше одного слова*/

SELECT *, SUBSTRING_INDEX(department_name, ' ', 1)
FROM departments
WHERE department_name like '% %';

/* 7. Таблица Employees. Получить список всех сотрудников, которые пришли на работу в первый день месяца (любого)*/

SELECT *
FROM employees
WHERE DAY(hire_date) = 1;

/* 8. Таблица Countries. Для каждой страны показать регион в котором он находится: 1-Europe, 2-America, 3-Asia, 4-Africa (без Join)*/

SELECT c.country_id, c.country_name, r.region_name
FROM countries c
LEFT JOIN regions r on r.region_id = c.region_id;

/* 9. Таблица Employees. Получить уровень зарплаты каждого сотрудника: Меньше 5000 считается Low level, Больше или равно 5000 и меньше 10000 считается Normal level, Больше иои равно 10000 считается High level*/

SELECT *,
    CASE
        WHEN salary < 5000 THEN 'Low level'
        WHEN salary >= 5000 AND salary < 10000 THEN 'Normal level'
        WHEN salary >= 10000 THEN 'High level'
    END
        income_category
FROM employees;

/* 10. Таблица Employees. Получить репорт по department_id с минимальной и максимальной зарплатой, с ранней и поздней датой прихода на работу и с количествов сотрудников. Сорировать по количеству сотрудников (по убыванию)*/

SELECT department_id,
    MIN(salary),
    MAX(salary),
    MIN(hire_date),
    MAX(hire_date),
    COUNT(employee_id)
FROM employees
GROUP BY department_id
ORDER BY COUNT(employee_id) DESC;

/* 11. Таблица Employees. Сколько сотрудников которые работают в одном и тоже отделе и получают одинаковую зарплату? */

SELECT department_id, COUNT(employee_id) AS head_count
FROM employees
GROUP BY department_id, salary
HAVING head_count > 1

/* 12. Таблица Employees. Сколько в таблице сотрудников, имена которых начинаются с одной и той же буквы? Сортировать по количеству. Показывать только те строки, где количество сотрудников больше 1*/

SELECT SUBSTRING(first_name, 1, 1) AS first_letter, COUNT(employee_id) AS head_count
FROM employees
GROUP BY first_letter
HAVING head_count > 1
ORDER BY head_count DESC;

/* 13. Таблица Employees. Получить список department_id и округленную среднюю зарплату работников в каждом департаменте. */

SELECT department_id, ROUND(AVG(salary)) AS avg_salary
FROM employees
GROUP BY department_id;

/* 14. Таблица Countries. Получить список region_id, сумма длин всех country_name в котором больше 60ти */

SELECT region_id, region_name, SUM(LENGTH(country_name)) AS total_length
FROM
(SELECT r.region_id, r.region_name, c.country_name
FROM regions r
LEFT JOIN countries c on r.region_id = c.region_id) AS ext_regions
GROUP BY region_id
HAVING total_length > 60;

/* 15. Таблица Employees, Departaments, Locations, Countries, Regions. Получить список регионов и количество сотрудников в каждом регионе */

SELECT r.region_name, COUNT(e.employee_id)
FROM employees e
LEFT JOIN departments d on e.department_id = d.department_id
LEFT JOIN locations l on d.location_id = l.location_id
LEFT JOIN countries c on l.country_id = c.country_id
LEFT JOIN regions r on c.region_id = r.region_id
GROUP BY r.region_name;

/* 16. Таблица Employees. Показать всех менеджеров, которые имеют в подчинении больше 6ти сотрудников*/

SELECT e2.first_name, COUNT(*)  AS leader_of
FROM employees e1
JOIN employees e2 on e1.manager_id = e2.employee_id
GROUP BY e2.first_name
HAVING leader_of > 6;

/* 17. Таблица Employees. Показать всех сотрудников, у которых нет ни кого в подчинении*/

SELECT first_name, last_name
FROM employees e1
LEFT JOIN
(SELECT manager_id, COUNT(*)  AS leader_of
FROM employees
GROUP BY manager_id) e2 on e1.employee_id=e2.manager_id
WHERE e2.leader_of IS NULL;

/* 18. Таблица Employees, Departaments. Показать все департаменты, в которых работают больше пяти сотрудников*/

SELECT department_name, COUNT(employee_id) AS emp_dep
FROM employees
JOIN departments d on d.department_id = employees.department_id
GROUP BY department_name
HAVING emp_dep > 5;

/* 19. Таблица Employees. Получить список сотрудников с зарплатой большей средней зарплаты всех сотрудников.*/

SELECT first_name, last_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) from employees);

/* 20. Таблица Employees, Departaments. Показать сотрудников, которые работают в департаменте IT*/

SELECT first_name, last_name
FROM employees e
LEFT JOIN departments d on e.department_id = d.department_id
WHERE department_name = 'IT';