# Webhook Code Formatter

This webhook system automatically checks and fixes Python code formatting issues using `isort` and `black`, then commits the changes to git.

## Features

- **Automatic Code Formatting**: Runs `isort` and `black` on all Python files
- **Auto-commit**: Automatically commits formatting changes
- **Git Integration**: Works as a pre-commit hook
- **HTTP Webhook Server**: Can be triggered via HTTP requests
- **Configurable**: Customizable settings via JSON config
- **Safe Operation**: Checks git status before making changes

## Quick Start

### 1. Setup

Run the setup script to install dependencies and configure git hooks:

```bash
python3 setup_webhook.py
```

This will:
- Install required dependencies (`isort`, `black`)
- Create a pre-commit git hook
- Generate configuration files
- Create a webhook runner script

### 2. Manual Usage

Run the formatter manually:

```bash
# Check and fix issues, then commit
./run_webhook.sh

# Only check for issues (don't fix)
./run_webhook.sh --check-only

# Custom commit message
python3 webhook_formatter.py --commit-message "Fix code formatting"
```

### 3. HTTP Webhook Server

Start the webhook server for HTTP triggers:

```bash
# Basic server
python3 webhook_server.py

# Custom host and port
python3 webhook_server.py --host 0.0.0.0 --port 8080

# With webhook secret for security
python3 webhook_server.py --webhook-secret "your-secret-key"
```

#### HTTP Endpoints

- `GET /health` - Health check
- `GET /trigger?check_only=true` - Manual trigger (check only)
- `GET /trigger` - Manual trigger (fix and commit)
- `POST /webhook` - Webhook endpoint (for GitHub/GitLab)

## Configuration

### webhook_config.json

```json
{
  "isort": {
    "profile": "black",
    "line_length": 88,
    "include_trailing_comma": true
  },
  "black": {
    "line_length": 88,
    "target_version": ["py38", "py39", "py310", "py311"]
  },
  "git": {
    "auto_commit": true,
    "commit_message_template": "Auto-format: Fix isort and black issues in {file_count} files"
  }
}
```

### pyproject.toml

The setup script also creates a `pyproject.toml` file for `isort` and `black` configuration that will be used by the tools.

## Git Integration

### Pre-commit Hook

The setup script automatically installs a pre-commit hook that runs the formatter before each commit. This ensures all committed code is properly formatted.

### Manual Git Integration

You can also run the formatter manually before committing:

```bash
# Check what would be changed
python3 webhook_formatter.py --check-only

# Fix and commit
python3 webhook_formatter.py
```

## GitHub/GitLab Integration

### GitHub Webhook

1. Go to your repository settings
2. Add a webhook with URL: `http://your-server:8080/webhook`
3. Set content type to `application/json`
4. Add secret if using `--webhook-secret`
5. Select "Push" events

### GitLab Webhook

1. Go to your project settings → Webhooks
2. Add URL: `http://your-server:8080/webhook`
3. Select "Push events"
4. Add secret token if using `--webhook-secret`

## Command Line Options

### webhook_formatter.py

```bash
python3 webhook_formatter.py [OPTIONS]

Options:
  --project-root PATH     Root directory of the project (default: current)
  --check-only           Only check for issues, don't fix them
  --commit-message TEXT  Custom commit message for auto-commits
  --config PATH          Path to configuration file
  --verbose              Enable verbose logging
  --help                 Show help message
```

### webhook_server.py

```bash
python3 webhook_server.py [OPTIONS]

Options:
  --host TEXT            Host to bind to (default: 0.0.0.0)
  --port INTEGER         Port to bind to (default: 8080)
  --project-root PATH    Root directory of the project (default: current)
  --webhook-secret TEXT  Secret for webhook signature verification
  --verbose              Enable verbose logging
  --help                 Show help message
```

## Safety Features

- **Git Status Check**: Ensures working directory is clean before making changes
- **File Tracking**: Only commits files that were actually changed
- **Error Handling**: Comprehensive error handling and logging
- **Timeout Protection**: Prevents hanging operations
- **Signature Verification**: Optional webhook signature verification

## Troubleshooting

### Common Issues

1. **"Not in a git repository"**
   - Make sure you're in a git repository
   - Run `git init` if needed

2. **"There are uncommitted changes"**
   - Commit or stash your changes first
   - The formatter requires a clean working directory

3. **"webhook_formatter.py not found"**
   - Make sure you're running from the project root
   - Check that the file exists

4. **Permission denied on webhook script**
   - Make the script executable: `chmod +x run_webhook.sh`

### Debug Mode

Run with verbose logging to see detailed information:

```bash
python3 webhook_formatter.py --verbose
python3 webhook_server.py --verbose
```

## File Structure

```
project/
├── webhook_formatter.py      # Main formatter script
├── webhook_server.py         # HTTP webhook server
├── setup_webhook.py          # Setup script
├── webhook_config.json       # Configuration file
├── pyproject.toml            # isort/black configuration
├── run_webhook.sh            # Convenience script
└── .git/hooks/pre-commit     # Git pre-commit hook
```

## Requirements

- Python 3.8+
- Git repository
- isort >= 5.12.0
- black >= 23.0.0

## License

This webhook formatter is part of the Lenovo Sensor Monitor project and follows the same license terms.