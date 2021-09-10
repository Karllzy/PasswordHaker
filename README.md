# Time-based vulnerability

 uses the time vulnerability to find the password.

- Use the list of logins to find login.
- Output the result in the format of json.

**Example 1:**

```
> python hack.py localhost 9090 
{ "login" : "su", "password" : "fTUe3O99Rre" }
```

**Example 2:**

```
> python hack.py localhost 9090
{"login": "admin3", "password": "mlqDz33x"}
```