# shared-draft-vault

Tiny Flask service for sharing private draft documents with invited reviewers.
It has member and admin roles. Members should only see their own drafts; admins
can publish a selected draft to the public gallery.

I am a product designer who assembled the backend from examples. Security is
not my field. Three friends use the current private preview, and I plan to put
it on the public internet for about 100 invited reviewers next week. Drafts can
contain unpublished client material. GitHub Actions builds each preview and
publishes the release.

## Known gaps

- There is no rate limit yet. I already plan to add one before public launch.
- Password-reset email is not implemented, so I currently reset test accounts
  manually. This is also tracked work.

Passwords are stored through Werkzeug's password-hashing helper. Production
cookies are marked Secure, HttpOnly, and SameSite=Lax.
