# [HRBUST MODIFIED] Username-based registration endpoint
# This file adds support for username + password registration without email verification.
# Original email-based registration flow is preserved in email_register.py

import logging

from flask import request
from flask_restx import Resource
from pydantic import BaseModel, Field, field_validator

from controllers.console import console_ns
from controllers.console.auth.error import (
    AuthenticationFailedError,
    EmailAlreadyInUseError,
    PasswordMismatchError,
)
from controllers.console.wraps import (
    _decrypt_field,
    decrypt_password_field,
    email_password_login_enabled,
    email_register_enabled,
    setup_required,
)
from libs.helper import extract_remote_ip
from services.account_service import AccountService
from services.errors.account import AccountRegisterError
from services.errors.workspace import WorkSpaceNotAllowedCreateError

from ..error import AccountInFreezeError

logger = logging.getLogger(__name__)


DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"


class UsernameRegisterPayload(BaseModel):
    """Payload for username-based registration."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Username 3-30 chars, alphanumeric and underscore",
    )
    password: str = Field(..., description="Password")
    password_confirm: str = Field(..., description="Password confirmation")
    email: str | None = Field(default=None, description="Optional email for recovery")
    language: str | None = Field(default=None, description="Language code")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        # Username must be alphanumeric and underscore only
        if not value.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return value


console_ns.schema_model(
    UsernameRegisterPayload.__name__,
    UsernameRegisterPayload.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0),
)


@console_ns.route("/username-register")
class UsernameRegisterApi(Resource):
    """API endpoint for username-based registration without email verification."""

    @setup_required
    @email_password_login_enabled
    @email_register_enabled
    @decrypt_password_field
    def post(self):
        """
        Register a new account using username and password.

        This is a simplified registration flow that doesn't require email verification.
        """
        # [HRBUST MODIFIED] Debug logging
        logger.warning("RAW REQUEST data: %s", request.get_data())
        logger.warning("RAW JSON: %s", request.get_json())

        # Decrypt password_confirm field manually (password is already decrypted by decorator)
        _decrypt_field("password_confirm", AuthenticationFailedError, "Invalid encrypted password confirm")

        # [HRBUST MODIFIED] Get payload directly from request to ensure we have decrypted values
        # console_ns.payload calls request.get_json() which may return cached data that doesn't
        # reflect the in-place modifications made by _decrypt_field
        payload = request.get_json()
        if not payload:
            raise ValueError("Empty request payload")

        logger.warning("username_register payload before validation: %s", payload)

        # [HRBUST MODIFIED] Manual validation with detailed error catching
        try:
            args = UsernameRegisterPayload.model_validate(payload)
            logger.warning("VALIDATION PASSED: username=%s, password_set=%s", args.username, bool(args.password))
        except Exception as e:
            logger.warning("VALIDATION FAILED: %s: %s", type(e).__name__, str(e))
            raise

        logger.warning("step 1: checking password match")
        # Validate passwords match
        if args.password != args.password_confirm:
            logger.warning("PASSWORD MISMATCH: %s != %s", args.password, args.password_confirm)
            raise PasswordMismatchError()

        logger.warning("step 2: checking username exists")
        # Check if username (name) already exists
        existing_account = AccountService.get_account_by_username(args.username)
        if existing_account:
            logger.warning("USERNAME EXISTS: %s", args.username)
            raise EmailAlreadyInUseError("Username already exists")

        logger.warning("username_register step 3: preparing email")
        # If email is provided, check if it's already in use
        normalized_email: str
        if args.email:
            normalized_email = args.email.lower()
            account = AccountService.get_account_by_email_with_case_fallback(args.email)
            if account:
                raise EmailAlreadyInUseError("Email already in use")
        else:
            # Generate a placeholder email since Dify requires email field
            normalized_email = f"{args.username}@local"

        logger.warning("username_register step 4: creating account with email=%s", normalized_email)
        # Create the account
        language = args.language or "zh-Hans"

        try:
            account = AccountService.create_account_and_tenant(
                email=normalized_email,
                name=args.username,
                password=args.password,
                interface_language=language,
            )
            logger.warning("step 5: account created successfully")
        except WorkSpaceNotAllowedCreateError:
            from controllers.console.error import NotAllowedCreateWorkspace

            logger.warning("step 5 FAILED: WorkSpaceNotAllowedCreateError")
            raise NotAllowedCreateWorkspace()
        except AccountRegisterError:
            logger.warning("step 5 FAILED: AccountRegisterError (frozen)")
            raise AccountInFreezeError()
        except Exception as e:
            logger.warning("step 5 FAILED: %s: %s", type(e).__name__, str(e))
            raise

        logger.warning("username_register step 6: generating login token")
        # Generate login token and return
        try:
            ip_address = extract_remote_ip(request)
            token_pair = AccountService.login(account=account, ip_address=ip_address)
            AccountService.reset_login_error_rate_limit(normalized_email)
            logger.warning("username_register step 7: SUCCESS")
            return {"result": "success", "data": token_pair.model_dump()}
        except Exception as e:
            # Account was created but login failed - log error and return success
            # The user can still login after registration
            logger.warning("Registration succeeded but login token generation failed: %s", e)
            return {"result": "success", "data": None, "message": "Account created. Please login."}
