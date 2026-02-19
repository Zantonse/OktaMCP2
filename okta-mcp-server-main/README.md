<div align="center">

![Okta MCP Server](assets/thumbnail.png)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.8-brightgreen.svg)](https://python.org/)

</div>

[MCP (Model Context Protocol)](https://modelcontextprotocol.io/introduction) is an open protocol introduced by Anthropic that standardizes how large language models communicate with external tools, resources or remote services.

> [!CAUTION]
> **Beta Software Notice: This software is currently in beta and is provided AS IS without any warranties.**
>
> - Features, APIs, and functionality may change at any time without notice
> - Not recommended for production use or critical workloads
> - Support during the beta period is limited
> - Issues and feedback can be reported through the [GitHub issue tracker](https://github.com/okta/okta-mcp-server/issues)
>
> By using this beta software, you acknowledge and accept these conditions.

The Okta MCP Server integrates with LLMs and AI agents, allowing you to perform various Okta management operations using natural language. For instance, you could simply ask Claude Desktop to perform Okta management operations:

- > Create a new user and add them to the Engineering group
- > Show me all failed login attempts from the last 24 hours
- > List all applications that haven't been used in the past month

**Empower your LLM Agents to Manage your Okta Organization**

This server is an [Model Context Protocol](https://modelcontextprotocol.io/introduction) server that provides seamless integration with Okta's Admin Management APIs. It allows LLM agents to interact with Okta in a programmatic way, enabling automation and enhanced management capabilities.

## Key Features

* **LLM-Driven Okta Management:** Allows your LLM agents to perform administrative tasks within your Okta environment based on natural language instructions.
* **Secure Authentication:** Supports both Device Authorization Grant for interactive use and Private Key JWT for secure, automated server-to-server communication.
* **Integration with Okta Admin Management APIs:** Leverages the official Okta APIs to ensure secure and reliable interaction with your Okta org.
* **Extensible Architecture:** Designed to be easily extended with new functionalities and support for additional Okta API endpoints.
* **Comprehensive Tool Support:** 195 tools across 24 domains — users, groups, applications, policies, security monitoring, and more.

This MCP server utilizes [Okta's Python SDK](https://github.com/okta/okta-sdk-python) to communicate with the Okta APIs, ensuring a robust and well-supported integration.

## 🚀 Getting Started

**Prerequisites:**

- [Python 3.8+](https://python.org/downloads)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- [Claude Desktop](https://claude.ai/download) or any other [MCP Client](https://modelcontextprotocol.io/clients)
- [Okta](https://okta.com/) account with appropriate permissions

<br/>

### Install the Okta MCP Server

Install Okta MCP Server and configure it to work with your preferred MCP Client.

**Claude Desktop with all tools**

1. Clone and install the server:
   ```bash
   git clone https://github.com/okta/okta-mcp-server.git
   cd okta-mcp-server
   uv sync
   ```

2. Configure Claude Desktop by adding the following to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "okta-mcp-server": {
         "command": "uv",
         "args": [
           "run",
           "--directory",
           "/path/to/okta-mcp-server",
           "okta-mcp-server"
         ],
         "env": {
           "OKTA_ORG_URL": "<OKTA_ORG_URL>",
           "OKTA_CLIENT_ID": "<OKTA_CLIENT_ID>",
           "OKTA_SCOPES": "<OKTA_SCOPES>",
           "OKTA_PRIVATE_KEY": "<PRIVATE_KEY_IF_NEEDED>",
           "OKTA_KEY_ID": "<KEY_ID_IF_NEEDED>"
         }
       }
     }
   }
   ```

**VS Code**

Add the following to your VS Code `settings.json`:
```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "description": "Okta Organization URL (e.g., https://dev-123456.okta.com)",
        "id": "OKTA_ORG_URL"
      },
      {
        "type": "promptString",
        "description": "Okta Client ID",
        "id": "OKTA_CLIENT_ID",
        "password": true
      },
      {
        "type": "promptString",
        "description": "Okta Scopes (separated by whitespace, e.g., 'okta.users.read okta.groups.manage')",
        "id": "OKTA_SCOPES"
      },
      {
        "type": "promptString",
        "description": "Okta Private Key. Required for 'browserless' auth.",
        "id": "OKTA_PRIVATE_KEY",
        "password": true
      },
      {
        "type": "promptString",
        "description": "Okta Key ID (KID) for the private key. Required for 'browserless' auth.",
        "id": "OKTA_KEY_ID",
        "password": true
      }
    ],
    "servers": {
      "okta-mcp-server": {
        "command": "uv",
        "args": [
          "run",
          "--directory",
          "/path/to/the/okta-mcp-server",
          "okta-mcp-server"
        ],
        "env": {
          "OKTA_ORG_URL": "${input:OKTA_ORG_URL}",
          "OKTA_CLIENT_ID": "${input:OKTA_CLIENT_ID}",
          "OKTA_SCOPES": "${input:OKTA_SCOPES}",
          "OKTA_PRIVATE_KEY": "${input:OKTA_PRIVATE_KEY}",
          "OKTA_KEY_ID": "${input:OKTA_KEY_ID}"
        }
      }
    }
  }
}
```

**Other MCP Clients**

To use Okta MCP Server with any other MCP Client, you can manually add this configuration to the client and restart for changes to take effect:

```json
{
  "mcpServers": {
    "okta-mcp-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/okta-mcp-server",
        "okta-mcp-server"
      ],
      "env": {
        "OKTA_ORG_URL": "<OKTA_ORG_URL>",
        "OKTA_CLIENT_ID": "<OKTA_CLIENT_ID>",
        "OKTA_SCOPES": "<OKTA_SCOPES>",
        "OKTA_PRIVATE_KEY": "<PRIVATE_KEY_IF_NEEDED>",
        "OKTA_KEY_ID": "<KEY_ID_IF_NEEDED>"
      }
    }
  }
}
```

### Authenticate with Okta

The server supports two authentication methods. Choose the one that best fits your use case.

**Method 1: Device Authorization Grant (Interactive)**

1. In your Okta org, create a **new App Integration**.
2. Select **OIDC - OpenID Connect** and **Native Application**.
3. Under **Grant type**, ensure **Device Authorization** is checked.
4. Go to the Okta API Scopes tab and Grant permissions for the APIs you need (e.g., okta.users.read, okta.groups.manage).
5. Save the application and copy the **Client ID**.
6. **Documentation:** [Okta Device Authorization Grant Guide](https://developer.okta.com/docs/guides/device-authorization-grant/main/)

**Method 2: Private Key JWT (Browserless)**

1. **Create App:** In your Okta org, create a **new App Integration**. Select **API Services**. Save the app and copy the **Client ID**.
2. **Configure Client Authentication:**
   * On the app's **General** tab, find the **Client Credentials** section and click **Edit**.
   * Disable **Require Demonstrating Proof of Possession (DPoP) header in token requests**.
   * Select **Public key / Private key** for the authentication method.
3. **Add a Public Key:** You have two options for adding a key.
   * **Option A: Generate Key in Okta (Recommended)**
     1. In the **Public keys** section, click **Add key**.
     2. In the dialog, choose **Generate new key**.
     3. Okta will instantly generate a key pair. **Download or save the private key** (`private.pem`) and store it securely.
     4. Copy the **Key ID (KID)** displayed for the newly generated key.
   * **Option B: Use Your Own Key**
     1. Generate a key pair locally using the following `openssl` commands:
        ```bash
        # Generate a 2048-bit RSA private key
        openssl genpkey -algorithm RSA -out private.pem -pkeyopt rsa_keygen_bits:2048
        
        # Extract the public key from the private key
        openssl rsa -in private.pem -pubout -out public.pem
        ```
     2. Click **Add key** and paste the contents of your **public key** (`public.pem`) into the dialog.
     3. Copy the **Key ID (KID)** displayed for the key you added.
4. **Grant API Scopes:** Go to the **Okta API Scopes** tab and **Grant** permissions for the APIs you need.
5. **Assign Admin Roles:** To avoid `403 Forbidden` errors, go to the **Admin roles** tab and assign the **Super Administrator** role to this application.

### Verify your integration

Restart your MCP Client (Claude Desktop, VS Code, etc.) and ask it to help you manage your Okta tenant:

> Show me the users in my Okta organization

## 🛠️ Supported Tools

The Okta MCP Server provides **195 tools across 24 domains** for LLMs to interact with your Okta tenant.

### Overview

| Category | Module | Tools | Description |
|----------|--------|------:|-------------|
| **Identity** | Users | 17 | User CRUD, lifecycle management, password operations |
| **Identity** | Groups | 10 | Group CRUD, membership management |
| **Identity** | Schemas | 8 | User profile schema and custom attributes |
| **Applications** | Applications | 16 | App CRUD, user/group assignment |
| **Applications** | Trusted Origins | 8 | CORS trusted origin management |
| **Security** | Policies | 14 | Policy and policy rule management |
| **Security** | Roles | 10 | Admin role assignment and targeting |
| **Security** | Authorization Servers | 14 | OAuth server, scopes, claims, policies |
| **Security** | Authenticators | 8 | Authenticator and method configuration |
| **Security** | Factors | 6 | MFA factor enrollment and verification |
| **Security** | Device Assurance | 6 | Device posture policy management |
| **Monitoring** | System Logs | 1 | System log retrieval with filtering |
| **Monitoring** | Behavior Rules | 8 | Behavior detection rule management |
| **Monitoring** | ThreatInsight | 2 | Threat detection configuration |
| **Monitoring** | Sessions | 5 | Session lifecycle and revocation |
| **Infrastructure** | Network Zones | 8 | IP/dynamic zone management |
| **Infrastructure** | Event Hooks | 9 | Webhook event hook management |
| **Infrastructure** | Identity Providers | 8 | External IdP configuration |
| **Infrastructure** | Inline Hooks | 9 | Logic injection hook management |
| **Infrastructure** | Profile Mappings | 3 | Attribute mapping management |
| **Infrastructure** | Devices | 5 | Device inventory and management |
| **Infrastructure** | Brands | 12 | Brand, theme, and email customization |
| **Administration** | Features | 4 | Org feature flag management |
| **Administration** | Org Settings | 4 | Organization configuration |

---

### Identity Management

#### Users

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_users` | List all users with pagination | `search`, `filter_expr`, `q`, `limit`, `after`, `fetch_all` |
| `get_user` | Get a user by ID | `user_id` |
| `create_user` | Create a new user | `profile` |
| `update_user` | Update user profile | `user_id`, `profile` |
| `deactivate_user` | Deactivate a user | `user_id` |
| `delete_deactivated_user` | Permanently delete a deactivated user | `user_id` |
| `activate_user` | Activate a user | `user_id` |
| `reactivate_user` | Reactivate a deprovisioned user | `user_id` |
| `suspend_user` | Suspend a user | `user_id` |
| `unsuspend_user` | Unsuspend a user | `user_id` |
| `unlock_user` | Unlock a locked-out user | `user_id` |
| `expire_password` | Expire a user's password | `user_id` |
| `expire_password_with_temp_password` | Expire password and generate temporary | `user_id` |
| `reset_password` | Reset a user's password | `user_id`, `send_email` |
| `list_user_groups` | List groups a user belongs to | `user_id`, `limit`, `after`, `fetch_all` |
| `list_user_apps` | List apps linked to a user | `user_id`, `limit`, `after`, `fetch_all` |
| `get_user_profile_attributes` | List all supported profile attributes | _(none)_ |

#### Groups

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_groups` | List all groups with pagination | `search`, `filter_expr`, `q`, `limit`, `after`, `fetch_all` |
| `get_group` | Get a group by ID | `group_id` |
| `create_group` | Create a new group | `profile` |
| `update_group` | Update group profile | `group_id`, `profile` |
| `delete_group` | Delete a group (confirmation required) | `group_id` |
| `confirm_delete_group` | Confirm and execute group deletion | `group_id`, `confirmation` |
| `list_group_users` | List users in a group | `group_id`, `limit`, `after`, `fetch_all` |
| `list_group_apps` | List apps assigned to a group | `group_id` |
| `add_user_to_group` | Add a user to a group | `group_id`, `user_id` |
| `remove_user_from_group` | Remove a user from a group | `group_id`, `user_id` |

#### Schemas

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_user_schema` | Get default user profile schema | _(none)_ |
| `get_user_schema_by_type` | Get schema for a specific user type | `type_id` |
| `list_user_types` | List all user types | _(none)_ |
| `add_user_schema_property` | Add a custom attribute | `property_name`, `type_id`, `property_config` |
| `update_user_schema_property` | Update a custom attribute | `property_name`, `type_id`, `property_config` |
| `remove_user_schema_property` | Remove a custom attribute | `property_name`, `type_id` |
| `get_app_user_schema` | Get app-specific user schema | `app_id` |
| `update_app_user_schema` | Update app-specific user schema | `app_id`, `schema_config` |

---

### Application Management

#### Applications

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_applications` | List all applications with pagination | `q`, `filter_expr`, `expand`, `limit`, `after`, `fetch_all` |
| `get_application` | Get an application by ID | `app_id`, `expand` |
| `create_application` | Create a new application | `app_config`, `activate` |
| `update_application` | Update an application | `app_id`, `app_config` |
| `delete_application` | Delete an application (confirmation required) | `app_id` |
| `confirm_delete_application` | Confirm and execute app deletion | `app_id`, `confirmation` |
| `activate_application` | Activate an application | `app_id` |
| `deactivate_application` | Deactivate an application | `app_id` |
| `list_application_users` | List users assigned to an app | `app_id`, `limit`, `after`, `fetch_all` |
| `get_application_user` | Get a specific app user | `app_id`, `user_id` |
| `assign_user_to_application` | Assign a user to an app | `app_id`, `user_id`, `app_user_config` |
| `remove_user_from_application` | Remove a user from an app | `app_id`, `user_id` |
| `list_application_groups` | List groups assigned to an app | `app_id`, `limit`, `after`, `fetch_all` |
| `get_application_group` | Get a specific app group | `app_id`, `group_id` |
| `assign_group_to_application` | Assign a group to an app | `app_id`, `group_id` |
| `remove_group_from_application` | Remove a group from an app | `app_id`, `group_id` |

#### Trusted Origins

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_trusted_origins` | List all trusted origins | `q`, `limit`, `after`, `fetch_all` |
| `get_trusted_origin` | Get a trusted origin by ID | `origin_id` |
| `create_trusted_origin` | Create a new trusted origin | `name`, `origin`, `scopes` |
| `update_trusted_origin` | Update a trusted origin | `origin_id`, `name`, `scopes` |
| `delete_trusted_origin` | Delete a trusted origin (confirmation required) | `origin_id` |
| `confirm_delete_trusted_origin` | Confirm and execute deletion | `origin_id`, `confirmation` |
| `activate_trusted_origin` | Activate a trusted origin | `origin_id` |
| `deactivate_trusted_origin` | Deactivate a trusted origin | `origin_id` |

---

### Security & Access Control

#### Policies

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_policies` | List all policies | `type`, `status`, `q`, `limit`, `after` |
| `get_policy` | Get a policy by ID | `policy_id` |
| `create_policy` | Create a new policy | `policy_data` |
| `update_policy` | Update a policy | `policy_id`, `policy_data` |
| `delete_policy` | Delete a policy | `policy_id` |
| `activate_policy` | Activate a policy | `policy_id` |
| `deactivate_policy` | Deactivate a policy | `policy_id` |
| `list_policy_rules` | List rules for a policy | `policy_id` |
| `get_policy_rule` | Get a specific policy rule | `policy_id`, `rule_id` |
| `create_policy_rule` | Create a rule for a policy | `policy_id`, `rule_data` |
| `update_policy_rule` | Update a policy rule | `policy_id`, `rule_id`, `rule_data` |
| `delete_policy_rule` | Delete a policy rule | `policy_id`, `rule_id` |
| `activate_policy_rule` | Activate a policy rule | `policy_id`, `rule_id` |
| `deactivate_policy_rule` | Deactivate a policy rule | `policy_id`, `rule_id` |

#### Roles

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_roles` | List all available admin role types | _(none)_ |
| `list_user_roles` | List roles assigned to a user | `user_id` |
| `list_group_roles` | List roles assigned to a group | `group_id` |
| `assign_role_to_user` | Assign an admin role to a user | `user_id`, `role_type` |
| `unassign_role_from_user` | Remove a role from a user | `user_id`, `role_id` |
| `assign_role_to_group` | Assign an admin role to a group | `group_id`, `role_type` |
| `unassign_role_from_group` | Remove a role from a group | `group_id`, `role_id` |
| `list_user_role_targets` | List targets for a scoped role | `user_id`, `role_id`, `target_type` |
| `add_user_role_target` | Add a target to a scoped role | `user_id`, `role_id`, `target_type`, `target_id` |
| `remove_user_role_target` | Remove a target from a scoped role | `user_id`, `role_id`, `target_type`, `target_id` |

#### Authorization Servers

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_authorization_servers` | List all authorization servers | `q`, `limit`, `after`, `fetch_all` |
| `get_authorization_server` | Get an auth server by ID | `auth_server_id` |
| `create_authorization_server` | Create a new auth server | `name`, `description`, `audiences` |
| `update_authorization_server` | Update an auth server | `auth_server_id`, `name`, `description`, `audiences` |
| `delete_authorization_server` | Delete an auth server (confirmation required) | `auth_server_id` |
| `confirm_delete_authorization_server` | Confirm and execute deletion | `auth_server_id`, `confirmation` |
| `activate_authorization_server` | Activate an auth server | `auth_server_id` |
| `deactivate_authorization_server` | Deactivate an auth server | `auth_server_id` |
| `list_auth_server_policies` | List policies for an auth server | `auth_server_id`, `limit`, `after`, `fetch_all` |
| `create_auth_server_policy` | Create a policy for an auth server | `auth_server_id`, `policy_config` |
| `list_auth_server_scopes` | List scopes for an auth server | `auth_server_id`, `limit`, `after`, `fetch_all` |
| `create_auth_server_scope` | Create a scope for an auth server | `auth_server_id`, `name`, `description` |
| `list_auth_server_claims` | List claims for an auth server | `auth_server_id`, `limit`, `after`, `fetch_all` |
| `create_auth_server_claim` | Create a claim for an auth server | `auth_server_id`, `name`, `claim_type`, `value` |

#### Authenticators

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_authenticators` | List all authenticators | _(none)_ |
| `get_authenticator` | Get authenticator details | `authenticator_id` |
| `activate_authenticator` | Activate an authenticator | `authenticator_id` |
| `deactivate_authenticator` | Deactivate an authenticator | `authenticator_id` |
| `list_authenticator_methods` | List methods for an authenticator | `authenticator_id` |
| `get_authenticator_method` | Get a specific method | `authenticator_id`, `method_type` |
| `activate_authenticator_method` | Activate a method | `authenticator_id`, `method_type` |
| `deactivate_authenticator_method` | Deactivate a method | `authenticator_id`, `method_type` |

#### Factors

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_user_factors` | List MFA factors for a user | `user_id` |
| `get_user_factor` | Get a specific factor | `user_id`, `factor_id` |
| `enroll_factor` | Enroll a new MFA factor | `user_id`, `factor_type`, `provider`, `profile` |
| `activate_factor` | Activate an enrolled factor | `user_id`, `factor_id`, `pass_code` |
| `reset_factor` | Remove a factor | `user_id`, `factor_id` |
| `verify_factor` | Verify a factor challenge | `user_id`, `factor_id`, `pass_code` |

#### Device Assurance

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_device_assurance_policies` | List all device assurance policies | _(none)_ |
| `get_device_assurance_policy` | Get a policy by ID | `policy_id` |
| `create_device_assurance_policy` | Create a new policy | `name`, `platform`, `policy_config` |
| `update_device_assurance_policy` | Update a policy | `policy_id`, `policy_config` |
| `delete_device_assurance_policy` | Delete a policy (confirmation required) | `policy_id` |
| `confirm_delete_device_assurance_policy` | Confirm and execute deletion | `policy_id`, `confirmation` |

---

### Security Monitoring

#### System Logs

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_logs` | Retrieve system logs with filtering | `since`, `until`, `filter_expr`, `q`, `limit`, `after`, `fetch_all` |

#### Behavior Detection Rules

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_behavior_rules` | List all behavior detection rules | _(none)_ |
| `get_behavior_rule` | Get a behavior rule by ID | `behavior_id` |
| `create_behavior_rule` | Create a new behavior rule | `name`, `behavior_type`, `settings` |
| `update_behavior_rule` | Update a behavior rule | `behavior_id`, `name`, `behavior_type`, `settings` |
| `delete_behavior_rule` | Delete a behavior rule (confirmation required) | `behavior_id` |
| `confirm_delete_behavior_rule` | Confirm and execute deletion | `behavior_id`, `confirmation` |
| `activate_behavior_rule` | Activate a behavior rule | `behavior_id` |
| `deactivate_behavior_rule` | Deactivate a behavior rule | `behavior_id` |

#### ThreatInsight

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_threat_insight_configuration` | Get current ThreatInsight config | _(none)_ |
| `update_threat_insight_configuration` | Update ThreatInsight config | `action`, `exclude_zones` |

#### Sessions

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_session` | Get a session by ID | `session_id` |
| `create_session` | Create a new session | `session_token` |
| `refresh_session` | Refresh/extend a session | `session_id` |
| `close_session` | Close a specific session | `session_id` |
| `revoke_user_sessions` | Revoke all sessions for a user | `user_id` |

---

### Infrastructure & Integrations

#### Network Zones

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_network_zones` | List all network zones | `q`, `limit`, `after`, `fetch_all` |
| `get_network_zone` | Get a network zone by ID | `zone_id` |
| `create_network_zone` | Create a new network zone | `name`, `zone_type`, `gateways`, `proxies` |
| `update_network_zone` | Update a network zone | `zone_id`, `name`, `gateways`, `proxies` |
| `delete_network_zone` | Delete a zone (confirmation required) | `zone_id` |
| `confirm_delete_network_zone` | Confirm and execute deletion | `zone_id`, `confirmation` |
| `activate_network_zone` | Activate a network zone | `zone_id` |
| `deactivate_network_zone` | Deactivate a network zone | `zone_id` |

#### Event Hooks

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_event_hooks` | List all event hooks | _(none)_ |
| `get_event_hook` | Get an event hook by ID | `event_hook_id` |
| `create_event_hook` | Create a new event hook | `name`, `url`, `events`, `headers` |
| `update_event_hook` | Update an event hook | `event_hook_id`, `name`, `url`, `events`, `headers` |
| `delete_event_hook` | Delete an event hook (confirmation required) | `event_hook_id` |
| `confirm_delete_event_hook` | Confirm and execute deletion | `event_hook_id`, `confirmation` |
| `activate_event_hook` | Activate an event hook | `event_hook_id` |
| `deactivate_event_hook` | Deactivate an event hook | `event_hook_id` |
| `verify_event_hook` | Verify an event hook endpoint | `event_hook_id` |

#### Inline Hooks

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_inline_hooks` | List all inline hooks | `type` |
| `get_inline_hook` | Get an inline hook by ID | `inline_hook_id` |
| `create_inline_hook` | Create a new inline hook | `name`, `hook_type`, `url`, `headers` |
| `update_inline_hook` | Update an inline hook | `inline_hook_id`, `name`, `url`, `headers` |
| `delete_inline_hook` | Delete an inline hook (confirmation required) | `inline_hook_id` |
| `confirm_delete_inline_hook` | Confirm and execute deletion | `inline_hook_id`, `confirmation` |
| `activate_inline_hook` | Activate an inline hook | `inline_hook_id` |
| `deactivate_inline_hook` | Deactivate an inline hook | `inline_hook_id` |
| `execute_inline_hook` | Execute an inline hook for testing | `inline_hook_id`, `payload` |

#### Profile Mappings

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_profile_mappings` | List all profile mappings | `source_id`, `target_id`, `after`, `limit` |
| `get_profile_mapping` | Get a profile mapping by ID | `mapping_id` |
| `update_profile_mapping` | Update a profile mapping | `mapping_id`, `mapping_config` |

#### Identity Providers

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_identity_providers` | List all identity providers | `q`, `type_filter`, `limit`, `after`, `fetch_all` |
| `get_identity_provider` | Get an IdP by ID | `idp_id` |
| `create_identity_provider` | Create a new IdP | `name`, `idp_type`, `protocol`, `policy` |
| `update_identity_provider` | Update an IdP | `idp_id`, `name`, `protocol`, `policy` |
| `delete_identity_provider` | Delete an IdP (confirmation required) | `idp_id` |
| `confirm_delete_identity_provider` | Confirm and execute deletion | `idp_id`, `confirmation` |
| `activate_identity_provider` | Activate an IdP | `idp_id` |
| `deactivate_identity_provider` | Deactivate an IdP | `idp_id` |

#### Devices

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_devices` | List all devices | _(none)_ |
| `get_device` | Get a device by ID | `device_id` |
| `delete_device` | Delete a device (confirmation required) | `device_id` |
| `confirm_delete_device` | Confirm and execute deletion | `device_id`, `confirmation` |
| `list_user_devices` | List devices for a user | `user_id` |

#### Brands

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_brands` | List all brands | _(none)_ |
| `get_brand` | Get a brand by ID | `brand_id` |
| `update_brand` | Update a brand | `brand_id`, `brand_config` |
| `list_brand_themes` | List themes for a brand | `brand_id` |
| `get_brand_theme` | Get a specific theme | `brand_id`, `theme_id` |
| `update_brand_theme` | Update a brand theme | `brand_id`, `theme_id`, `theme_config` |
| `upload_brand_logo` | Upload a logo image | `brand_id`, `theme_id`, `logo_file_path` |
| `upload_brand_favicon` | Upload a favicon image | `brand_id`, `theme_id`, `favicon_file_path` |
| `get_email_template` | Get an email template | `brand_id`, `template_name` |
| `update_email_template` | Update an email template | `brand_id`, `template_name`, `template_config` |
| `get_signin_page` | Get sign-in page customization | `brand_id` |
| `update_signin_page` | Update sign-in page customization | `brand_id`, `page_config` |

---

### Administration

#### Features

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_features` | List all org features | _(none)_ |
| `get_feature` | Get a feature by ID | `feature_id` |
| `enable_feature` | Enable a feature | `feature_id`, `mode` |
| `disable_feature` | Disable a feature | `feature_id`, `mode` |

#### Org Settings

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `get_org_settings` | Get organization settings | _(none)_ |
| `update_org_settings` | Update organization settings | `settings` |
| `get_org_contact_types` | Get available contact types | _(none)_ |
| `get_org_contact_user` | Get contact user by type | `contact_type` |

## 🔐 Authentication

The Okta MCP Server uses the Okta Management API and requires authentication to access your Okta tenant.

### Authentication Flow

The server uses OAuth 2.0 device authorization flow for secure authentication with Okta, or Private Key JWT for browserless authentication. Your credentials are managed securely and are never exposed in plain text.

### Initial Setup

The MCP Server will automatically initiate the appropriate authentication flow based on your configuration:

- **Device Authorization Grant**: Interactive browser-based authentication
- **Private Key JWT**: Browserless authentication using client credentials

> [!NOTE]
> Device authorization flow is not supported for **private cloud** tenants. Private Cloud users should use Private Key JWT authentication with client credentials.

> [!IMPORTANT]
> Using the MCP Server will consume Management API rate limits according to your subscription plan. Refer to the [Rate Limit Policy](https://developer.okta.com/docs/reference/rate-limits/) for more information.

## 🩺 Troubleshooting

When encountering issues with the Okta MCP Server, several troubleshooting options are available to help diagnose and resolve problems.

### 🐞 Debug Mode

Enable debug mode for more detailed logging:

```bash
export OKTA_LOG_LEVEL=DEBUG
```

> [!TIP]
> Debug mode is particularly useful when troubleshooting connection or authentication issues.

### 🚨 Common Issues

1. **Authentication Failures**
   - Ensure you have the correct permissions in your Okta tenant
   - Verify your `OKTA_ORG_URL`, `OKTA_CLIENT_ID`, and `OKTA_SCOPES` are correct
   - Check that your application has the necessary API scopes granted

2. **MCP Client Can't Connect to the Server**
   - Restart your MCP client after installation
   - Verify the server path is correct in your configuration
   - Check that `uv` is installed and accessible in your PATH

3. **API Errors or Permission Issues**
   - Enable debug mode with `export OKTA_LOG_LEVEL=DEBUG`
   - Verify your Okta application has the required scopes
   - Ensure your application has appropriate admin roles assigned
   - Check the Okta System Log for detailed error information

4. **"Claude's response was interrupted..." Error**
   - This typically happens when Claude hits its context-length limit
   - Try to be more specific and keep queries concise
   - Break large requests into smaller, focused operations

> [!TIP]
> Most connection issues can be resolved by restarting both the server and your MCP client.

## 👨‍💻 Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/okta/okta-mcp-server.git
cd okta-mcp-server

# Install dependencies
uv sync

# Run the server directly
uv run okta-mcp-server
```

### Development Scripts

```bash
# Run with debug logs enabled
OKTA_LOG_LEVEL=DEBUG uv run okta-mcp-server

# Run tests
uv run pytest

# Install in development mode
uv pip install -e .
```

> [!NOTE]
> This server requires [Python 3.8 or higher](https://python.org/downloads) and [uv](https://docs.astral.sh/uv/).

## 🔒 Security

The Okta MCP Server prioritizes security:

- Credentials are managed through secure authentication flows
- No sensitive information is stored in plain text  
- Authentication uses OAuth 2.0 device authorization flow or Private Key JWT
- Supports fine-grained API scope permissions
- Easy credential management through environment variables

> [!IMPORTANT]
> For security best practices, always review the permissions requested during the authentication process to ensure they align with your security requirements.

> [!CAUTION]
> Always use the principle of least privilege when granting API scopes to your Okta application.

## 🧪 Security Scanning

We recommend regularly scanning this server, and any other MCP-compatible servers you deploy, with community tools built to surface protocol-level risks and misconfigurations.

These scanners help identify issues across key vulnerability classes including: server implementation bugs, tool definition and lifecycle risks, interaction and data flow weaknesses, and configuration or environment gaps.

If you discover a vulnerability, please follow our [responsible disclosure process](https://www.okta.com/security/).

## 💬 Feedback and Contributing

We appreciate feedback and contributions to this project! Before you get started, please see:

- [Okta's general contribution guidelines](CONTRIBUTING.md)

### Reporting Issues

To provide feedback or report a bug, please [raise an issue on our issue tracker](https://github.com/okta/okta-mcp-server/issues).

### Vulnerability Reporting

Please do not report security vulnerabilities on the public GitHub issue tracker. Please follow the [responsible disclosure process](https://www.okta.com/security/).

## 📄 License

This project is licensed under the Apache 2.0 license. See the [LICENSE](LICENSE) file for more info.

---

## What is Okta?

<p align="center">
  <picture>
    <img alt="Okta Logo" src="assets/logo.png" width="150">
  </picture>
</p>
<p align="center">
  Okta is the leading independent identity provider. To learn more checkout <a href="https://www.okta.com/why-okta/">Why Okta?</a>
</p>

Copyright © 2025-Present, Okta, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

