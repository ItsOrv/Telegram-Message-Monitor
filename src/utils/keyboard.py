# src/keyboards/keyboard.py

from telethon import Button

def main_menu_keyboard():
    """
    Returns the main menu keyboard layout.
    """
    return [
        [Button.inline("Add Account", b'add_account')],
        [Button.inline("Show Accounts", b'show_accounts')],
        [Button.inline("Update Groups", b'update_groups')],
        [
            Button.inline('Add Keyword', b'add_keyword'),
            Button.inline('Remove Keyword', b'remove_keyword')
        ],
        [
            Button.inline('Ignore User', b'ignore_user'),
            Button.inline('Remove Ignore', b'remove_ignore_user')
        ],
        [Button.inline('Stats', b'show_stats')]
    ]
