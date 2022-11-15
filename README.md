# Boilerplate

## Project's structure

<details>
<summary>Click to collapse/fold.</summary>

```
.
├── admin.py ············ admin panel (sqladmin) initialization
├── alembic ············· alembic's data, what were generated during init, but can be updated
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions ········ generated migrations by alembic
├── alembic.ini ········· alembic's config
├── createuser.py ······· script for adding new user
├── db
│   ├── models.py ······· db's models
│   └── session.py ······ params for connection to db
├── exceptions.py
├── main.py ············· main code for starting app
├── permissions.py
├── README.md ··········· you're here
├── requirements.txt
├── run.sh ·············· script for starting app
├── schemas ············· strawberry schemas (graphql part)
│   ├── mutations.py
│   ├── queries.py
│   └── types.py
├── services ············ main backend logic
│   ├── files.py
│   └── users.py
├── settings.py ········· app settings
├── templates ··········· templates for pages
│   ├── login.html
│   └── main.html
├── tests
│   └── migrations ······ migrations' test (for avoiding conflicts after migrations)
└── utils.py ············ contains methods for token and password
```

</details>

## Alembic

**Create migration**:

```
alembic revision --autogenerate -m "Comment"
```

*Recommendation*: use '{000}_comment' format for comments.

**Migrate to last**:

```
alembic upgrade head
```

**Downgrade to base**:

```
alembic downgrade base
```

Sometimes you need to correct migrations manually, it's normal case — that why we use migration test before migrating. For example, [enum issue](#enum-autogeneration).

### Enum autogeneration

There is problem with autogeneration of enums in db (at least on PostgreSQL), so we need to rewrite enums adding. Before:


```
def upgrade() -> None:
    …
    sa.Column('gender', postgresql.ENUM('MALE', 'FEMALE', 'OTHER', name='genderenum'), nullable=True),
    …
```

After:

```
def upgrade() -> None:
    …
    gender_enum = postgresql.ENUM('MALE', 'FEMALE', 'OTHER', name='genderenum', create_type=False)
    gender_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('user', sa.Column('gender', gender_enum, nullable=True))
    …

def downgrade() -> None:
    …
    gender_enum = sa.Enum(name='genderenum')
    gender_enum.drop(op.get_bind(), checkfirst=True)
    …
```

### Other things

- Run [migrations test](#migrations-test) before pushing
- Alembic doesn't add in migration default values, use `server_default` manually.

## User adding

Use `createuser.py` for adding new user in table. Remember, that this is not the same user as admin panel's user.

## Migrations test

This `test_stairway.py` can check that all migrations are possible to upgrade and downgrade. Should be started before upgrade. Use `python -m pytest tests/` to run test.
