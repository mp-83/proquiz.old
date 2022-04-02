

#### Notes

Database is created by dockerfile


```
docker-compose exec server alembic upgrade head && docker-compose exec server alembic current

insert into users(email,password_hash,create_timestamp,is_admin) value ('admin@proquiz.io', '$2b$12$2WYFlv4DFQm4Wu5BP13I5epD3Oiv74VuZxDyZbXvMwAgH3CHZx8h6', '2022-04-02T18:48:07.916501',true);

'admin@proquiz.io'
"p@ssworth"

```
