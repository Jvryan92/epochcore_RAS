# RAS API Documentation

## Overview

EpochCore RAS (Recursive Autonomous Security) is offered as a Software-as-a-Service solution providing enterprise-grade security verification and cryptographic proof validation.

## Getting Started

1. Sign up for an API key at https://ras.epochcore.com
2. Install the RAS client library:
   ```bash
   pip install epochcore-ras-client
   ```

## Authentication

All API requests require authentication using a Bearer token:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" https://api.ras.epochcore.com/v1/status
```

## API Endpoints

### Security Verification

```http
POST /api/v1/verify
Authorization: Bearer YOUR_API_TOKEN

Response:
{
    "status": "success",
    "timestamp": "2025-08-29T01:33:40.170314+00:00",
    "details": {
        "success": true,
        "primary": true,
        "compatibility": true
    }
}
```

### Create Session

```http
POST /api/v1/sessions
Authorization: Bearer YOUR_API_TOKEN

Response:
{
    "token": "session_token",
    "expires": "2025-08-29T02:33:40.170314+00:00"
}
```

### Verify Proof

```http
POST /api/v1/proofs/verify
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json

{
    "block_data": "...",
    "block_index": 0,
    "proof": [...]
}

Response:
{
    "valid": true,
    "timestamp": "2025-08-29T01:33:40.170314+00:00"
}
```

### System Status

```http
GET /api/v1/status
Authorization: Bearer YOUR_API_TOKEN

Response:
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-08-29T01:33:40.170314+00:00"
}
```

## Rate Limits

- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise tier: Custom limits

## Support

For support inquiries:
- Email: support@epochcore.com
- Documentation: https://docs.ras.epochcore.com
- Status page: https://status.ras.epochcore.com
