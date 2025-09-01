# Telegram Bot API Middleware

## Overview

This project is a FastAPI-based middleware service that interfaces with a Telegram bot (@MYEYEINFO_bot) to provide phone number information lookup functionality. The service acts as a bridge between HTTP REST API requests and Telegram bot interactions, using the Pyrogram library to automate bot conversations. Users can make HTTP requests to get information about phone numbers, which are then processed by interacting with the underlying Telegram bot through automated message sending and button clicking.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
The system follows a modular architecture with clear separation of concerns:

- **FastAPI Application**: Serves as the main web framework providing REST API endpoints
- **Telegram Client Manager**: Handles Telegram API connections using Pyrogram library with session-based authentication
- **Bot Handler**: Manages interactions with the specific Telegram bot, including button clicking and message parsing
- **Configuration Management**: Centralized configuration handling with environment variable support

### Authentication & Session Management
The application uses Telegram's session string authentication mechanism:
- Pre-authenticated session strings eliminate the need for real-time phone verification
- Session persistence allows the service to maintain long-running connections
- API ID and API Hash provide application-level authentication with Telegram's servers

### API Design
RESTful API design with FastAPI:
- `/` endpoint for health checks and service status
- `/number_info` endpoint for phone number lookup with query parameter validation
- Automatic OpenAPI documentation generation
- JSON response format for consistent data exchange

### Bot Interaction Strategy
Automated bot conversation flow:
- Sends `/start` command to refresh bot menus
- Programmatically clicks inline keyboard buttons
- Handles response timeouts and error recovery
- Parses bot responses to extract relevant information

### Error Handling & Logging
Comprehensive error management:
- Structured logging throughout all components
- Graceful degradation for network failures
- Timeout handling for bot interactions
- Configuration validation on startup

## External Dependencies

### Core Framework Dependencies
- **FastAPI**: Web framework for building the REST API
- **Pyrogram**: Telegram MTProto API client library for bot interactions
- **asyncio**: Asynchronous programming support for concurrent operations

### Telegram Integration
- **Telegram Bot API**: Integration with @MYEYEINFO_bot for phone number lookups
- **Telegram Client API**: Direct interaction with Telegram's servers using MTProto protocol

### Configuration Requirements
- **Environment Variables**: API credentials, session strings, and service configuration
- **Session Management**: Persistent Telegram session for maintaining authenticated connections

### Runtime Environment
- **Python 3.7+**: Required for asyncio and modern Python features
- **Network Connectivity**: Stable internet connection for Telegram API communication
- **Port Configuration**: Configurable host and port settings for deployment flexibility