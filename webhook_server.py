#!/usr/bin/env python3
"""
Simple HTTP webhook server to trigger code formatting.
Can be used with GitHub webhooks, GitLab webhooks, or manual triggers.
"""

import os
import sys
import json
import logging
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import subprocess
from pathlib import Path
import hmac
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for webhook endpoints."""
    
    def __init__(self, *args, webhook_secret=None, project_root=".", **kwargs):
        self.webhook_secret = webhook_secret
        self.project_root = project_root
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        """Handle GET requests (health check, manual trigger)."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/health":
            self.send_health_response()
        elif parsed_path.path == "/trigger":
            self.handle_trigger_request(parsed_path.query)
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests (webhook triggers)."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/webhook":
            self.handle_webhook_request()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Send health check response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "service": "webhook-formatter",
            "project_root": self.project_root
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def handle_trigger_request(self, query_string):
        """Handle manual trigger requests."""
        query_params = parse_qs(query_string)
        check_only = query_params.get('check_only', ['false'])[0].lower() == 'true'
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Run formatter in a separate thread
        thread = threading.Thread(
            target=self.run_formatter,
            args=(check_only,)
        )
        thread.daemon = True
        thread.start()
        
        response = {
            "status": "triggered",
            "check_only": check_only,
            "message": "Formatter started in background"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def handle_webhook_request(self):
        """Handle webhook requests from Git providers."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Verify webhook signature if secret is provided
        if self.webhook_secret:
            signature = self.headers.get('X-Hub-Signature-256', '')
            if not self.verify_signature(post_data, signature):
                self.send_error(401, "Unauthorized")
                return
        
        # Parse webhook payload
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        
        # Check if this is a push event
        event_type = self.headers.get('X-GitHub-Event', '')
        if event_type == 'push':
            # Run formatter
            thread = threading.Thread(target=self.run_formatter, args=(False,))
            thread.daemon = True
            thread.start()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "received",
            "event_type": event_type,
            "message": "Webhook processed"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def verify_signature(self, payload, signature):
        """Verify webhook signature."""
        if not self.webhook_secret:
            return True
        
        expected_signature = 'sha256=' + hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def run_formatter(self, check_only=False):
        """Run the formatter script."""
        try:
            webhook_script = Path(__file__).parent / "webhook_formatter.py"
            command = [
                sys.executable,
                str(webhook_script),
                "--project-root", self.project_root
            ]
            
            if check_only:
                command.append("--check-only")
            
            logger.info(f"Running formatter: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("Formatter completed successfully")
            else:
                logger.error(f"Formatter failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Formatter timed out")
        except Exception as e:
            logger.error(f"Error running formatter: {e}")


def create_webhook_handler(webhook_secret, project_root):
    """Create a webhook handler with the given configuration."""
    def handler(*args, **kwargs):
        return WebhookHandler(*args, webhook_secret=webhook_secret, project_root=project_root, **kwargs)
    return handler


def main():
    """Main server function."""
    parser = argparse.ArgumentParser(description="Webhook server for code formatting")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to (default: 8080)"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Root directory of the project (default: current directory)"
    )
    parser.add_argument(
        "--webhook-secret",
        help="Secret for webhook signature verification"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verify project root
    project_root = Path(args.project_root).absolute()
    if not project_root.exists():
        logger.error(f"Project root does not exist: {project_root}")
        sys.exit(1)
    
    # Check if webhook formatter exists
    webhook_script = project_root / "webhook_formatter.py"
    if not webhook_script.exists():
        logger.error(f"webhook_formatter.py not found in {project_root}")
        sys.exit(1)
    
    # Create webhook handler
    handler = create_webhook_handler(args.webhook_secret, str(project_root))
    
    # Start server
    server = HTTPServer((args.host, args.port), handler)
    
    logger.info(f"Starting webhook server on {args.host}:{args.port}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Health check: http://{args.host}:{args.port}/health")
    logger.info(f"Manual trigger: http://{args.host}:{args.port}/trigger")
    logger.info(f"Webhook endpoint: http://{args.host}:{args.port}/webhook")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down webhook server...")
        server.shutdown()


if __name__ == "__main__":
    main()