# SGR Coin Calculator API
Version 0.1
The backend and API for the SGR Coin Calculator

## Made with

- Python 3.13
- Flask
- uv
- Postgres 17.6

## Todo

- link docs from docs folder to this readme
- create a list of .env variables that need to exist  inc company cut for now
- add note that swagger is on `http://localhost:5000/api/swagger-ui`
- add note about cleardowndb script :: be in venv, update env vars for db url, run it, then run the seed script below to setup the default rank that's needed
- change member.status to member.active so the bool is more accurate
- add notes in creation on adding in a default rank to the rank table -> doing it with a simple insert into as it's not a big seed. TODO: look into making it part of the initial migration script in future, add it's name, position etc to constants for testing consistency
- review and make consisten uuid.UUID or from uuid import UUID

```
INSERT INTO ranks (id, name, position, share)
VALUES ('11111111-1111-1111-1111-111111111111', 'default', 99, 0)
ON CONFLICT (id) DO NOTHING;
```

The initial migration sets up everything
The add default migration adds the default rank