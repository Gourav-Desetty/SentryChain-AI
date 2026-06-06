"""Compatibility module for the older API import path.

The source-of-truth FastAPI application lives in
`src.SentryChain.backend.app`. This module re-exports it so existing
deployment commands that still reference `src.SentryChain.api.app:app`
continue to work.
"""

from src.SentryChain.backend.app import app
