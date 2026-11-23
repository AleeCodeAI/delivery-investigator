# Supabase Database Configuration

This document records database-level functionality configured directly in Supabase that is not currently represented in the FastAPI codebase.

The configuration described here uses PostgreSQL trigger functions and triggers to automate profile creation and invitation management.

## 1. Automatic Profile Creation

### Purpose

Whenever a new user is created through Supabase Authentication, a corresponding record is automatically inserted into the `public.profiles` table, including the user's full name.

This keeps the authentication user record and application profile record synchronized.

### Where the name comes from

The FastAPI sign-up endpoint passes the person's name to Supabase as user metadata when it creates the user:

```python
"user_metadata": {"full_name": data.full_name.strip()}
```

Supabase stores this in `auth.users.raw_user_meta_data`, for example:

```json
{
  "full_name": "Sarah Chenagzi",
  "email_verified": true
}
```

The metadata key is `full_name` (not `name`). The trigger function reads this key and copies it into `public.profiles.name`.

### Trigger function: `handle_new_user()`

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.profiles (user_id, email, name, created_at)
    VALUES (
        NEW.id,
        NEW.email,
        NULLIF(TRIM(NEW.raw_user_meta_data ->> 'full_name'), ''),
        NEW.created_at
    );

    RETURN NEW;
END;
$$;
```

**How it works**

- `RETURNS TRIGGER` declares the function as a PostgreSQL trigger function.
- `LANGUAGE plpgsql` specifies the procedural language used by the function.
- `SECURITY DEFINER` makes the function execute with the privileges of its owner.
- `SET search_path = ''` avoids relying on a potentially unsafe default schema search path. Database objects are referenced with their schema names.
- `NEW` represents the row being inserted into `auth.users`.
- `NEW.raw_user_meta_data ->> 'full_name'` reads the `full_name` value from the user metadata as text.
- `TRIM(...)` removes leading and trailing spaces, and `NULLIF(..., '')` stores `NULL` instead of an empty string when the name is missing or blank.
- The function copies the new user's ID, email, name, and creation timestamp into `public.profiles`.
- `RETURN NEW` returns the row that caused the trigger to execute.

### Trigger: `on_auth_user_created`

```sql
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_user();
```

**How it works**

- `AFTER INSERT ON auth.users` runs the trigger after a new authentication user has been inserted.
- `FOR EACH ROW` runs it once for every inserted user.
- `EXECUTE FUNCTION` invokes `public.handle_new_user()`.

The trigger itself did not need to change when the name was added. Updating the function with `CREATE OR REPLACE` is enough, because the trigger keeps calling the same function. Do not re-run `CREATE TRIGGER`, since it fails if the trigger already exists.

### Backfilling existing users (one-time)

Users created before the function was updated have an empty profile name. This one-time query copies the name from their metadata. It only fills profiles where `name` is still empty, so it will not overwrite existing names:

```sql
UPDATE public.profiles p
SET name = u.raw_user_meta_data ->> 'full_name'
FROM auth.users u
WHERE p.user_id = u.id
  AND p.name IS NULL
  AND u.raw_user_meta_data ->> 'full_name' IS NOT NULL;
```

**Result:** Every newly created authentication user automatically receives a corresponding profile record, and the profile's name is populated from `full_name` when the sign-up request provides it.

---

## 2. Delete the Associated Auth User When an Invitation Is Deleted

### Purpose

When an invitation is deleted from `public.invitations`, the associated user is also deleted from `auth.users`.

This is intended to keep invitation removal and authentication-account removal synchronized.

### Trigger function: `delete_invited_user()`

```sql
CREATE OR REPLACE FUNCTION public.delete_invited_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    DELETE FROM auth.users
    WHERE email = OLD.email;

    RETURN OLD;
END;
$$;
```

**How it works**

- `OLD` represents the existing invitation row that is about to be deleted.
- `OLD.email` retrieves the email address from that invitation.
- The `DELETE` statement removes the row from `auth.users` whose email matches the invitation's email.
- `RETURN OLD` returns the invitation row being deleted.

### Trigger: `on_invitation_deleted`

```sql
CREATE TRIGGER on_invitation_deleted
BEFORE DELETE ON public.invitations
FOR EACH ROW
EXECUTE FUNCTION public.delete_invited_user();
```

**How it works**

- `BEFORE DELETE ON public.invitations` runs the trigger before an invitation row is deleted.
- `FOR EACH ROW` runs it for every invitation being deleted.
- The trigger invokes `public.delete_invited_user()`.

**Result:** Deleting an invitation also attempts to delete the authentication user with the same email address.

---

## 3. Automatically Mark an Invitation as Used

### Purpose

When a new user is created in Supabase Authentication, the matching invitation is marked as used by setting its `status` field to `TRUE`.

This avoids requiring a separate API operation to update the invitation status after user creation.

### Trigger function: `mark_invitation_as_used()`

```sql
CREATE OR REPLACE FUNCTION public.mark_invitation_as_used()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    UPDATE public.invitations
    SET status = TRUE
    WHERE email = NEW.email;

    RETURN NEW;
END;
$$;
```

**How it works**

- `NEW` represents the newly inserted authentication user.
- `NEW.email` retrieves the email address of that user.
- The function updates the matching row in `public.invitations`.
- `SET status = TRUE` marks the invitation as used.
- `WHERE email = NEW.email` limits the update to the invitation with the same email address.
- `RETURN NEW` returns the authentication row that caused the trigger to execute.

### Trigger: `on_auth_user_created_mark_invitation`

```sql
CREATE TRIGGER on_auth_user_created_mark_invitation
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.mark_invitation_as_used();
```

**How it works**

- `AFTER INSERT ON auth.users` runs after a new authentication user has been inserted.
- `FOR EACH ROW` runs the trigger for every inserted user.
- The trigger invokes `public.mark_invitation_as_used()`.

**Result:** When a user is created in Supabase Authentication, the matching invitation is marked as used.

---

## 4. Overall Workflow

The triggers automate three operations:

1. **User creation:** Inserting a user into `auth.users` creates a corresponding profile in `public.profiles`, with the name taken from `raw_user_meta_data ->> 'full_name'`.
2. **Invitation status:** Inserting a user into `auth.users` marks the matching invitation as used.
3. **Invitation deletion:** Deleting an invitation from `public.invitations` attempts to delete the authentication user with the same email address.

Both user-creation triggers execute in response to the same `INSERT` operation on `auth.users`. They are independent triggers; neither function relies on the other running first.

## 5. Implementation Notes

- These functions and triggers are configured directly in Supabase PostgreSQL. They are not currently defined in the FastAPI codebase.
- `SECURITY DEFINER` causes a function to run with its owner's privileges. The function owner and permissions should therefore be managed carefully.
- Trigger operations run as part of the transaction that caused them to execute. If a trigger raises an error, the originating operation can fail as well.
- The invitation-deletion function identifies the authentication user by email. This assumes the email matches the intended account. A stable user ID is generally a safer identifier when one is available.
- The profile name is copied only when the user is created (the trigger runs on `INSERT`). If a name is changed later, `public.profiles.name` must be updated directly, because the trigger does not sync later changes.
- The sign-up request must send the name as `user_metadata.full_name`. If it is missing or blank, the profile name is stored as `NULL`.
- If the `name` column in `public.profiles` is ever made `NOT NULL`, `handle_new_user()` must provide a fallback value, or user creation will fail for users without a name.
- Because `mark_invitation_as_used()` runs when the user is inserted, the invitation is marked as used at account creation, even if the user has not yet confirmed their email.
