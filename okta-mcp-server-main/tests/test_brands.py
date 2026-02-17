# The Okta software accompanied by this notice is provided pursuant to the following terms:
# Copyright © 2025-Present, Okta, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or
# agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under
# the License.

"""Tests for the Okta brands management module."""

from unittest.mock import AsyncMock, patch

import pytest


class TestListBrands:
    """Tests for list_brands function."""

    @pytest.mark.asyncio
    async def test_list_brands_success(self, mock_context, mock_okta_client):
        """Test successfully listing all brands."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import list_brands

            result = await list_brands(ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_brands_error(self, mock_context):
        """Test error handling when listing brands fails."""
        mock_client = AsyncMock()
        mock_client.list_brands = AsyncMock(return_value=(None, None, "Okta API error"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import list_brands

            result = await list_brands(ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetBrand:
    """Tests for get_brand function."""

    @pytest.mark.asyncio
    async def test_get_brand_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving a specific brand."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import get_brand

            result = await get_brand(brand_id="bnd456", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "bnd456"

    @pytest.mark.asyncio
    async def test_get_brand_error(self, mock_context):
        """Test error handling when retrieving a brand fails."""
        mock_client = AsyncMock()
        mock_client.get_brand = AsyncMock(return_value=(None, None, "Brand not found"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import get_brand

            result = await get_brand(brand_id="invalid", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestUpdateBrand:
    """Tests for update_brand function."""

    @pytest.mark.asyncio
    async def test_update_brand_success(self, mock_context, mock_okta_client):
        """Test successfully updating a brand."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_brand

            result = await update_brand(
                brand_id="bnd456",
                ctx=mock_context,
                brand_config={"name": "Updated Brand"},
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "bnd456"

    @pytest.mark.asyncio
    async def test_update_brand_minimal(self, mock_context, mock_okta_client):
        """Test updating a brand with minimal parameters."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_brand

            result = await update_brand(
                brand_id="bnd456",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_update_brand_error(self, mock_context):
        """Test error handling when updating a brand fails."""
        mock_client = AsyncMock()
        mock_client.update_brand = AsyncMock(return_value=(None, None, "Update failed"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_brand

            result = await update_brand(
                brand_id="bnd456",
                ctx=mock_context,
                brand_config={"name": "Invalid"},
            )
            assert result.get("success") is False
            assert "error" in result


class TestListBrandThemes:
    """Tests for list_brand_themes function."""

    @pytest.mark.asyncio
    async def test_list_brand_themes_success(self, mock_context, mock_okta_client):
        """Test successfully listing themes for a brand."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import list_brand_themes

            result = await list_brand_themes(brand_id="bnd456", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert isinstance(result.get("data"), list)
            assert len(result.get("data")) > 0

    @pytest.mark.asyncio
    async def test_list_brand_themes_error(self, mock_context):
        """Test error handling when listing themes fails."""
        mock_client = AsyncMock()
        mock_client.list_brand_themes = AsyncMock(return_value=(None, None, "API error"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import list_brand_themes

            result = await list_brand_themes(brand_id="bnd456", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestGetBrandTheme:
    """Tests for get_brand_theme function."""

    @pytest.mark.asyncio
    async def test_get_brand_theme_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving a brand theme."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import get_brand_theme

            result = await get_brand_theme(brand_id="bnd456", theme_id="thm789", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "thm789"

    @pytest.mark.asyncio
    async def test_get_brand_theme_error(self, mock_context):
        """Test error handling when retrieving a theme fails."""
        mock_client = AsyncMock()
        mock_client.get_brand_theme = AsyncMock(return_value=(None, None, "Theme not found"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import get_brand_theme

            result = await get_brand_theme(brand_id="bnd456", theme_id="invalid", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestUpdateBrandTheme:
    """Tests for update_brand_theme function."""

    @pytest.mark.asyncio
    async def test_update_brand_theme_success(self, mock_context, mock_okta_client):
        """Test successfully updating a brand theme."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_brand_theme

            result = await update_brand_theme(
                brand_id="bnd456",
                theme_id="thm789",
                ctx=mock_context,
                theme_config={"primary_color_hex": "#ff0000"},
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").id == "thm789"

    @pytest.mark.asyncio
    async def test_update_brand_theme_minimal(self, mock_context, mock_okta_client):
        """Test updating a theme with minimal parameters."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_brand_theme

            result = await update_brand_theme(
                brand_id="bnd456",
                theme_id="thm789",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_update_brand_theme_error(self, mock_context):
        """Test error handling when updating a theme fails."""
        mock_client = AsyncMock()
        mock_client.update_brand_theme = AsyncMock(return_value=(None, None, "Update failed"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_brand_theme

            result = await update_brand_theme(
                brand_id="bnd456",
                theme_id="thm789",
                ctx=mock_context,
                theme_config={"primary_color_hex": "#invalid"},
            )
            assert result.get("success") is False
            assert "error" in result


class TestUploadBrandLogo:
    """Tests for upload_brand_logo function."""

    @pytest.mark.asyncio
    async def test_upload_brand_logo_file_not_found(self, mock_context, mock_okta_client):
        """Test error handling when logo file not found."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import upload_brand_logo

            result = await upload_brand_logo(
                brand_id="bnd456",
                theme_id="thm789",
                logo_file_path="/nonexistent/logo.png",
                ctx=mock_context,
            )
            assert result.get("success") is False
            assert "error" in result
            assert "not found" in result.get("error").lower()

    @pytest.mark.asyncio
    async def test_upload_brand_logo_error(self, mock_context):
        """Test error handling when logo upload fails."""
        mock_client = AsyncMock()
        mock_client.upload_brand_theme_logo = AsyncMock(return_value=(None, None, "Upload failed"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import upload_brand_logo
            import tempfile
            import os

            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".png") as tmp:
                tmp.write("fake image data")
                tmp_path = tmp.name

            try:
                result = await upload_brand_logo(
                    brand_id="bnd456",
                    theme_id="thm789",
                    logo_file_path=tmp_path,
                    ctx=mock_context,
                )
                assert result.get("success") is False
                assert "error" in result
            finally:
                os.unlink(tmp_path)


class TestUploadBrandFavicon:
    """Tests for upload_brand_favicon function."""

    @pytest.mark.asyncio
    async def test_upload_brand_favicon_file_not_found(self, mock_context, mock_okta_client):
        """Test error handling when favicon file not found."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import upload_brand_favicon

            result = await upload_brand_favicon(
                brand_id="bnd456",
                theme_id="thm789",
                favicon_file_path="/nonexistent/favicon.ico",
                ctx=mock_context,
            )
            assert result.get("success") is False
            assert "error" in result
            assert "not found" in result.get("error").lower()

    @pytest.mark.asyncio
    async def test_upload_brand_favicon_error(self, mock_context):
        """Test error handling when favicon upload fails."""
        mock_client = AsyncMock()
        mock_client.upload_brand_theme_favicon = AsyncMock(return_value=(None, None, "Upload failed"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import upload_brand_favicon
            import tempfile
            import os

            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ico") as tmp:
                tmp.write("fake favicon data")
                tmp_path = tmp.name

            try:
                result = await upload_brand_favicon(
                    brand_id="bnd456",
                    theme_id="thm789",
                    favicon_file_path=tmp_path,
                    ctx=mock_context,
                )
                assert result.get("success") is False
                assert "error" in result
            finally:
                os.unlink(tmp_path)


class TestGetEmailTemplate:
    """Tests for get_email_template function."""

    @pytest.mark.asyncio
    async def test_get_email_template_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving an email template."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import get_email_template

            result = await get_email_template(brand_id="bnd456", template_name="UserActivation", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "UserActivation"

    @pytest.mark.asyncio
    async def test_get_email_template_error(self, mock_context):
        """Test error handling when retrieving an email template fails."""
        mock_client = AsyncMock()
        mock_client.get_email_template = AsyncMock(return_value=(None, None, "Template not found"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import get_email_template

            result = await get_email_template(brand_id="bnd456", template_name="Invalid", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestUpdateEmailTemplate:
    """Tests for update_email_template function."""

    @pytest.mark.asyncio
    async def test_update_email_template_success(self, mock_context, mock_okta_client):
        """Test successfully updating an email template."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_email_template

            result = await update_email_template(
                brand_id="bnd456",
                template_name="UserActivation",
                ctx=mock_context,
                template_config={"subject": "Activate your account"},
            )
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").name == "UserActivation"

    @pytest.mark.asyncio
    async def test_update_email_template_minimal(self, mock_context, mock_okta_client):
        """Test updating an email template with minimal parameters."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_email_template

            result = await update_email_template(
                brand_id="bnd456",
                template_name="UserActivation",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_update_email_template_error(self, mock_context):
        """Test error handling when updating an email template fails."""
        mock_client = AsyncMock()
        mock_client.update_email_template = AsyncMock(return_value=(None, None, "Update failed"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_email_template

            result = await update_email_template(
                brand_id="bnd456",
                template_name="UserActivation",
                ctx=mock_context,
                template_config={"subject": "Invalid"},
            )
            assert result.get("success") is False
            assert "error" in result


class TestGetSignInPage:
    """Tests for get_signin_page function."""

    @pytest.mark.asyncio
    async def test_get_signin_page_success(self, mock_context, mock_okta_client):
        """Test successfully retrieving sign-in page customization."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import get_signin_page

            result = await get_signin_page(brand_id="bnd456", ctx=mock_context)
            assert result.get("success") is True
            assert "data" in result
            assert result.get("data").widget_version == "^5"

    @pytest.mark.asyncio
    async def test_get_signin_page_error(self, mock_context):
        """Test error handling when retrieving sign-in page fails."""
        mock_client = AsyncMock()
        mock_client.get_sign_in_page = AsyncMock(return_value=(None, None, "API error"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import get_signin_page

            result = await get_signin_page(brand_id="bnd456", ctx=mock_context)
            assert result.get("success") is False
            assert "error" in result


class TestUpdateSignInPage:
    """Tests for update_signin_page function."""

    @pytest.mark.asyncio
    async def test_update_signin_page_success(self, mock_context, mock_okta_client):
        """Test successfully updating sign-in page customization."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_signin_page

            result = await update_signin_page(
                brand_id="bnd456",
                ctx=mock_context,
                page_config={"widget_version": "^7"},
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_update_signin_page_minimal(self, mock_context, mock_okta_client):
        """Test updating sign-in page with minimal parameters."""
        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_okta_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_signin_page

            result = await update_signin_page(
                brand_id="bnd456",
                ctx=mock_context,
            )
            assert result.get("success") is True
            assert "data" in result

    @pytest.mark.asyncio
    async def test_update_signin_page_error(self, mock_context):
        """Test error handling when updating sign-in page fails."""
        mock_client = AsyncMock()
        mock_client.update_sign_in_page = AsyncMock(return_value=(None, None, "Update failed"))

        with patch(
            "okta_mcp_server.tools.brands.brands.get_okta_client",
            new_callable=AsyncMock,
            return_value=mock_client,
        ):
            from okta_mcp_server.tools.brands.brands import update_signin_page

            result = await update_signin_page(
                brand_id="bnd456",
                ctx=mock_context,
                page_config={"widget_version": "invalid"},
            )
            assert result.get("success") is False
            assert "error" in result
