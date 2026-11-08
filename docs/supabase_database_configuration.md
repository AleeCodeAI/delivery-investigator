# Supabase Database Configuration

This document records database-level functionality configured directly
in Supabase that is not currently represented in the FastAPI codebase.

The configuration described here uses PostgreSQL trigger functions and
triggers to automate profile creation and invitation management.

## 1. Automatic Profile Creation

### Purpose

Whenever a new user is created through Supabase Authentication, a
corresponding record is automatically inserted into the
`public.profiles` table.

This keeps the authentication user record and application profile record
synchronized.

### Trigger function: `handle_new_user()`

``` sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.profiles (user_id, email, created_at)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.created_at
    );

    RETURN NEW;
END;
$$;
```

**How it works**

-   `RETURNS TRIGGER` declares the function as a PostgreSQL trigger
    function.
-   `LANGUAGE plpgsql` specifies the procedural language used by the
    function.
-   `SECURITY DEFINER` makes the function execute with the privileges of
    its owner.
-   `SET search_path = ''` avoids relying on a potentially unsafe
    default schema search path. Database objects are referenced with
    their schema names.
-   `NEW` represents the row being inserted into `auth.users`.
-   The function copies the new user's ID, email, and creation timestamp
    into `public.profiles`.
-   `RETURN NEW` returns the row that caused the trigger to execute.

### Trigger: `on_auth_user_created`

``` sql
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_user();
```

**How it works**

-   `AFTER INSERT ON auth.users` runs the trigger after a new
    authentication user has been inserted.
-   `FOR EACH ROW` runs it once for every inserted user.
-   `EXECUTE FUNCTION` invokes `public.handle_new_user()`.

**Current limitation and planned improvement: profile name**

The `name` field in the newly created profile is currently left empty
because the `auth.users` record does not currently contain the person's
name.

When the frontend is implemented, it is expected to collect the person's
name and send it to Supabase Authentication as user metadata during
sign-up. The trigger function can then be updated to read the name from
`NEW.raw_user_meta_data` and insert it into `public.profiles.name`.

For example, the future implementation could use:

``` sql
INSERT INTO public.profiles (user_id, email, name, created_at)
VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data ->> 'name',
    NEW.created_at
);
```

This is a planned improvement, not part of the current trigger
implementation. The frontend must actually send the `name` metadata
field for this value to be populated.

**Result:** Every newly created authentication user automatically
receives a corresponding profile record. The profile's name is not
populated by the current implementation.

------------------------------------------------------------------------

## 2. Delete the Associated Auth User When an Invitation Is Deleted

### Purpose

When an invitation is deleted from `public.invitations`, the associated
user is also deleted from `auth.users`.

This is intended to keep invitation removal and authentication-account
removal synchronized.

### Trigger function: `delete_invited_user()`

``` sql
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

-   `OLD` represents the existing invitation row that is about to be
    deleted.
-   `OLD.email` retrieves the email address from that invitation.
-   The `DELETE` statement removes the row from `auth.users` whose email
    matches the invitation's email.
-   `RETURN OLD` returns the invitation row being deleted.

### Trigger: `on_invitation_deleted`

``` sql
CREATE TRIGGER on_invitation_deleted
BEFORE DELETE ON public.invitations
FOR EACH ROW
EXECUTE FUNCTION public.delete_invited_user();
```

**How it works**

-   `BEFORE DELETE ON public.invitations` runs the trigger before an
    invitation row is deleted.
-   `FOR EACH ROW` runs it for every invitation being deleted.
-   The trigger invokes `public.delete_invited_user()`.

**Result:** Deleting an invitation also attempts to delete the
authentication user with the same email address.

------------------------------------------------------------------------

## 3. Automatically Mark an Invitation as Used

### Purpose

When a new user is created in Supabase Authentication, the matching
invitation is marked as used by setting its `status` field to `TRUE`.

This avoids requiring a separate API operation to update the invitation
status after user creation.

### Trigger function: `mark_invitation_as_used()`

``` sql
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

-   `NEW` represents the newly inserted authentication user.
-   `NEW.email` retrieves the email address of that user.
-   The function updates the matching row in `public.invitations`.
-   `SET status = TRUE` marks the invitation as used.
-   `WHERE email = NEW.email` limits the update to the invitation with
    the same email address.
-   `RETURN NEW` returns the authentication row that caused the trigger
    to execute.

### Trigger: `on_auth_user_created_mark_invitation`

``` sql
CREATE TRIGGER on_auth_user_created_mark_invitation
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.mark_invitation_as_used();
```

**How it works**

-   `AFTER INSERT ON auth.users` runs after a new authentication user
    has been inserted.
-   `FOR EACH ROW` runs the trigger for every inserted user.
-   The trigger invokes `public.mark_invitation_as_used()`.

**Result:** When a user is created in Supabase Authentication, the
matching invitation is marked as used.

------------------------------------------------------------------------

## 4. Overall Workflow

The triggers automate three operations:

1.  **User creation:** Inserting a user into `auth.users` creates a
    corresponding profile in `public.profiles`.
2.  **Invitation status:** Inserting a user into `auth.users` marks the
    matching invitation as used.
3.  **Invitation deletion:** Deleting an invitation from
    `public.invitations` attempts to delete the authentication user with
    the same email address.

Both user-creation triggers execute in response to the same `INSERT`
operation on `auth.users`. They are independent triggers; neither
function relies on the other running first.

## 5. Implementation Notes

-   These functions and triggers are configured directly in Supabase
    PostgreSQL. They are not currently defined in the FastAPI codebase.
-   `SECURITY DEFINER` causes a function to run with its owner's
    privileges. The function owner and permissions should therefore be
    managed carefully.
-   Trigger operations run as part of the transaction that caused them
    to execute. If a trigger raises an error, the originating operation
    can fail as well.
-   The invitation-deletion function identifies the authentication user
    by email. This assumes the email matches the intended account. A
    stable user ID is generally a safer identifier when one is
    available.
-   The profile-name metadata integration is a planned change and has
    not yet been implemented.
