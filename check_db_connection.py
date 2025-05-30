"""Test script for PostgreSQL connection."""

import os
import sys

import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use a more linter-friendly way to print for this debug script
_print_to_stderr = print

def debug_print(message: str) -> None:
    """Prints messages to stderr for debugging this script."""
    _print_to_stderr(message, file=sys.stderr, flush=True)


def check_connection() -> None:
    """Checks the database connection and encoding using DATABASE_URL."""
    debug_print(f"psycopg2 version: {psycopg2.__version__}")
    debug_print(f"PYTHONUTF8 env var: {os.getenv('PYTHONUTF8')}")
    debug_print(f"PGCLIENTENCODING env var at start: {os.getenv('PGCLIENTENCODING')}")

    try:
        import locale
        preferred_encoding = locale.getpreferredencoding(False)
    except (ImportError, locale.Error):
        preferred_encoding = "unknown"
    debug_print(f"Default locale encoding: {preferred_encoding}")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        debug_print("DATABASE_URL not found in environment variables.")
        return

    debug_print(f"Attempting to connect using DSN: {database_url}")

    original_lc_messages = os.environ.get('LC_MESSAGES')
    original_pgclientencoding = os.environ.get('PGCLIENTENCODING')

    try:
        os.environ['LC_MESSAGES'] = 'C'  # Attempt to force ASCII error messages
        debug_print(f"Attempting with LC_MESSAGES=C (original value: '{original_lc_messages}')")

        # Connect using the DSN directly
        conn = psycopg2.connect(dsn=database_url, client_encoding='utf8')
        conn.autocommit = True
        cur = conn.cursor()

        debug_print("Connection successful!")

        cur.execute("SHOW client_encoding;")
        client_encoding_row = cur.fetchone()
        if client_encoding_row:
            debug_print(f"Client encoding for this session: {client_encoding_row[0]}")
        else:
            debug_print("Could not retrieve client_encoding.")

        cur.execute("SHOW server_encoding;")
        server_encoding_row = cur.fetchone()
        if server_encoding_row:
            debug_print(f"Server encoding: {server_encoding_row[0]}")
        else:
            debug_print("Could not retrieve server_encoding.")

        cur.close()
        conn.close()
        debug_print("Connection closed.")

    except psycopg2.OperationalError as op_err:
        debug_print(f"A psycopg2.OperationalError occurred: {op_err}")
        debug_print(f"  Original error message (str): {str(op_err)}")

        if hasattr(op_err, 'diag') and op_err.diag:
            debug_print(
                f"  Diagnostics: code={op_err.diag.sqlstate}, " # <--- Исправлено sqlstate_code на sqlstate
                f"message={op_err.diag.message_primary}"
            )
        else:
            debug_print("  No diagnostics available (op_err.diag is None or empty).")

        if hasattr(op_err, 'pgerror') and op_err.pgerror:
            pgerror_val = op_err.pgerror
            debug_print(f"  PGError (raw): {pgerror_val!r}")
            if isinstance(pgerror_val, bytes):
                for enc in ['windows-1251', 'cp866', 'koi8-r', 'iso8859-5', 'utf-8']:
                    try:
                        decoded_pgerror = pgerror_val.decode(enc)
                        debug_print(f"  PGError decoded with {enc}: {decoded_pgerror}")
                        break
                    except UnicodeDecodeError:
                        debug_print(f"  PGError failed to decode with {enc}")
            else:
                debug_print(f"  PGError (str): {str(pgerror_val)}")
        else:
            debug_print("  No pgerror attribute or it's empty.")

    except Exception as e:
        debug_print(f"An unexpected error occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
    finally:
        # Восстанавливаем PGCLIENTENCODING в исходное состояние или удаляем, если его не было
        if original_pgclientencoding is not None:
            os.environ['PGCLIENTENCODING'] = original_pgclientencoding
            debug_print(f"Restored PGCLIENTENCODING to '{original_pgclientencoding}'.")
        elif 'PGCLIENTENCODING' in os.environ: # Если мы его установили, а его не было
            del os.environ['PGCLIENTENCODING']
            debug_print("Removed PGCLIENTENCODING as it was not originally set.")

        if original_lc_messages is not None:
            os.environ['LC_MESSAGES'] = original_lc_messages
            debug_print(f"Restored LC_MESSAGES to '{original_lc_messages}'.")
        else:
            if os.getenv('LC_MESSAGES') == 'C':
                del os.environ['LC_MESSAGES']
                debug_print("Removed temporary LC_MESSAGES=C setting (was not originally set).")


if __name__ == "__main__":
    check_connection()
