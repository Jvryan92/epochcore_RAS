# EpochCore RAS API Documentation

## Overview
The EpochCore RAS provides a comprehensive API for managing recursive autonomous software systems.

## Endpoints

### Agent Management
- `GET /api/agents` - List all agents
- `POST /api/agents/sync` - Synchronize agent registry
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}/health` - Update agent health status

### System Operations
- `GET /api/system/status` - Get system status
- `POST /api/system/validate` - Validate system integrity
- `POST /api/system/backup` - Create system backup

### Recursive Improvement
- `GET /api/recursive/status` - Get recursive improvement status
- `POST /api/recursive/trigger` - Trigger recursive improvements
- `GET /api/recursive/engines` - List all engines

## Authentication
All API endpoints require authentication via API key or OAuth token.

## Rate Limiting
API calls are limited to 1000 requests per hour per authenticated user.
