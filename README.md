Павлов Алексей Игоревич
-----------------------

(46.) Разработка приложения для автоматизации технической поддержки (HelpDesk)
==============================================================================


```sql
DROP DATABASE IF EXISTS helpdesk WITH (FORCE);
CREATE DATABASE helpdesk WITH OWNER helpdesk ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE helpdesk TO helpdesk;
ALTER DATABASE helpdesk SET timezone TO 'Europe/Moscow';
ALTER USER helpdesk WITH PASSWORD 'P@ssw0rd';
commit;
```