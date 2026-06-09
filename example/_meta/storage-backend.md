backend: local
remote: none

---

# About this file

Records the storage backend the user chose at install time. The substrate-loading agent reads this on every session start to know which verb vocabulary to surface and which storage skill to delegate to.

For this example: `local` (the substrate lives on local disk only, no sync layer). A real solo install would more often be `box`; a real team install would more often be `git`.
