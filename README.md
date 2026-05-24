# peopleforce-mcp

MCP server for the [PeopleForce](https://peopleforce.io) HR platform. Exposes PeopleForce data as tools that Claude Code can call over HTTPS from any machine.

Transport: **Streamable HTTP + SSE** (not stdio). Runs as a Docker container on a remote VPS behind nginx + TLS.

---

## Tools available

| Tool | Description |
|---|---|
| `list_employees` | Paginated employee list, filterable by status / department / location |
| `get_employee` | Full employee profile by ID |
| `get_employee_by_email` | Convenience lookup by work email |
| `list_departments` | All departments |
| `list_vacations` | Time-off requests, filterable by employee / status / date range |
| `list_recruitments` | Open vacancies and recruitment pipeline |

---

## 1. Get a PeopleForce API key

1. Log in to your PeopleForce admin panel.
2. Go to **Settings → Integrations → API Keys**.
3. Click **Create API Key**, give it a name, and copy the key value.

---

## 2. Run locally with Docker

```bash
# Clone the repo
git clone <repo-url>
cd peopleforce-mcp

# Create your local secrets file (never committed)
cp .env.example .env
# Edit .env and fill in both values:
#   PEOPLEFORCE_API_KEY=...
#   MCP_SECRET_TOKEN=...   (generate with: python -c "import secrets; print(secrets.token_hex(32))")

# Build and start
docker compose up --build

# Verify health
curl http://localhost:8000/health
# → {"status":"ok"}
```

The server listens on `http://localhost:8000`. When running locally you can connect Claude Code to `http://localhost:8000/mcp`.

---

## 3. Deploy to an Amazon VPS

### Prerequisites
- Ubuntu 22.04 (or similar) EC2 instance
- Ports 80 and 443 open in the security group
- A domain name pointing to the server's public IP
- Docker + Docker Compose installed (`apt install docker.io docker-compose-plugin`)
- Nginx installed (`apt install nginx`)
- Certbot installed (`apt install certbot python3-certbot-nginx`)

### Steps

```bash
# 1. Copy files to the VPS (run on your local machine)
scp -r . ubuntu@YOUR_VPS_IP:/srv/peopleforce-mcp

# 2. SSH in
ssh ubuntu@YOUR_VPS_IP

# 3. Set environment variables (pick one approach)

# Option A — export in your shell session (lost on reboot)
export PEOPLEFORCE_API_KEY="..."
export MCP_SECRET_TOKEN="..."

# Option B — write a .env file on the server (not committed to git)
cat > /srv/peopleforce-mcp/.env <<EOF
PEOPLEFORCE_API_KEY=...
MCP_SECRET_TOKEN=...
EOF

# 4. Start the container
cd /srv/peopleforce-mcp
docker compose up -d

# 5. Configure nginx
#    Replace YOUR_DOMAIN in deploy/nginx.conf, then:
cp deploy/nginx.conf /etc/nginx/sites-available/peopleforce-mcp
sed -i 's/YOUR_DOMAIN/mcp.yourdomain.com/g' /etc/nginx/sites-available/peopleforce-mcp
ln -s /etc/nginx/sites-available/peopleforce-mcp /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 6. Obtain a TLS certificate
certbot --nginx -d mcp.yourdomain.com
# Certbot will modify nginx.conf automatically to add SSL directives.

# 7. Verify end-to-end
curl https://mcp.yourdomain.com/health
# → {"status":"ok"}
```

Docker Compose is configured with `restart: unless-stopped`, so the container restarts automatically after reboots or crashes.

---

## 4. Connect Claude Code

Add this to your project's `.mcp.json` (or to `~/.claude.json` under the `"mcpServers"` key for global access):

```json
{
  "mcpServers": {
    "peopleforce": {
      "type": "http",
      "url": "https://mcp.yourdomain.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_SECRET_TOKEN"
      }
    }
  }
}
```

Replace `mcp.yourdomain.com` with your domain and `YOUR_MCP_SECRET_TOKEN` with the value you set in `MCP_SECRET_TOKEN`.

Restart Claude Code after editing the config. The `peopleforce` server will appear in the tool list.

---

## 5. Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector \
  --transport http \
  --url https://mcp.yourdomain.com/mcp \
  --header "Authorization: Bearer YOUR_MCP_SECRET_TOKEN"
```

This opens an interactive UI where you can call each tool manually and inspect request/response payloads.

For local testing:

```bash
npx @modelcontextprotocol/inspector \
  --transport http \
  --url http://localhost:8000/mcp \
  --header "Authorization: Bearer YOUR_MCP_SECRET_TOKEN"
```

---

## Adding new tools

1. Add a method to `src/peopleforce.py` that calls the PeopleForce API.
2. Add a `@mcp.tool()` function in `src/server.py` that calls it via the client.
3. Rebuild: `docker compose up --build -d`.

No other files need to change.

---

## File structure

```
peopleforce-mcp/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── .env.example           # committed — placeholder values only
├── .gitignore             # excludes .env
├── requirements.txt
├── src/
│   ├── server.py          # FastMCP app + tool definitions
│   ├── peopleforce.py     # PeopleForce API client
│   └── auth.py            # Bearer token middleware
└── deploy/
    └── nginx.conf         # HTTPS reverse proxy config
```
