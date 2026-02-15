# Firefox NewUser

Script to run a Firefox instance with a dynamically created temporary user **exclusively in Wayland environments**. This project is specifically designed to work on **Gentoo Linux**; its functionality on other distributions is not guaranteed. The user and all their data are automatically deleted when the browser is closed, ensuring a clean and isolated session.

## Features

- **Total isolation:** Creates a dedicated system user (`firefox_newuser`) for the session.
- **Automatic cleanup:** Deletes the user, their group, and their `/home` directory after execution.
- **File synchronization:** Allows moving files downloaded or created during the session to a persistent directory before deletion.
- **Optimized for Wayland:** Uses native session management for modern environments.
- **Sound support:** Automatically bridges PipeWire/PulseAudio sockets and authentication cookies to ensure audio works out of the box.

## Requirements

- Python >= 3.10
- **root** privileges (the script will request them via `su` if run as a normal user).
- Firefox installed.

## Installation

If you use  **Gentoo Linux** you can find my ebuild en `https://github.com/turulomio/myportage/tree/master/www-client/firefox_newuser`.

You can install this package using pip or poetry
