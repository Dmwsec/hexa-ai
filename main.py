import argparse
import sys
import json
import logging
from enhanced_bug_bounty import EnhancedBugBountyClient
from config import Config

logging.basicConfig(level=logging.INFO)

def parse_args():
    parser = argparse.ArgumentParser(description="Enhanced Bug Bounty CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Search command
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--sort", default="default", help="Sort order")
    search_parser.add_argument("--ai-score", action="store_true", help="Enable AI scoring")
    
    # Code analysis command
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("--file", help="File to analyze")
    analyze_parser.add_argument("--code", help="Code to analyze")
    analyze_parser.add_argument("--output", help="Output file")
    
    # Token commands
    token_parser = subparsers.add_parser("token")
    token_subparsers = token_parser.add_subparsers(dest="token_action", required=True)
    
    token_subparsers.add_parser("get", help="Get current token")
    token_subparsers.add_parser("refresh", help="Refresh token")
    
    return parser.parse_args()

def main():
    args = parse_args()
    config = Config()
    client = EnhancedBugBountyClient(config)
    
    try:
        if args.command == "search":
            results = client.search(args.query, sort=args.sort)
            if args.ai_score:
                results = client._score_results(results)
            print(json.dumps(results, indent=2))
            
        elif args.command == "analyze":
            if args.file:
                with open(args.file) as f:
                    code = f.read()
            elif args.code:
                code = args.code
            else:
                raise ValueError("Either --file or --code must be specified")
                
            analysis = client.analyze_code(code)
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(analysis, f, indent=2)
            else:
                print(json.dumps(analysis, indent=2))
                
        elif args.command == "token":
            if args.token_action == "get":
                print(client.get_token())
            elif args.token_action == "refresh":
                client.refresh_token()
                print("Token refreshed successfully")
                
    except Exception as e:
        logging.error(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())
