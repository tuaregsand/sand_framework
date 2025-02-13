import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from agents.llm_client import LLMClient

logger = logging.getLogger(__name__)

class Web3DevAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.solana_docs_path = os.getenv("SOLANA_DOCS_PATH", "data/solana_docs")

    async def answer_dev_question(self, question: str) -> str:
        """Provide an answer to a Solana development question."""
        try:
            # First, search relevant documentation (placeholder for now)
            relevant_docs = self._search_documentation(question)
            
            # Construct prompt with context
            prompt = self._construct_dev_prompt(question, relevant_docs)
            
            # Generate answer using LLM
            answer = self.llm.generate_completion(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            return answer
        except Exception as e:
            logger.error(f"Error answering dev question: {str(e)}")
            raise

    async def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Solana project scaffold."""
        try:
            # Determine project type and framework
            if not framework:
                framework = "anchor"  # Default to Anchor framework
            
            # Generate project structure based on framework
            structure = self._generate_project_structure(name, framework)
            
            # Generate initialization commands
            commands = self._generate_init_commands(name, framework)
            
            # Return project information
            return {
                "name": name,
                "framework": framework,
                "path": f"./{name}",
                "structure": structure,
                "commands": commands,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise

    def _search_documentation(self, query: str) -> str:
        """Search through Solana documentation for relevant information."""
        # This is a placeholder - in a real implementation, this would:
        # 1. Use vector embeddings to search through documentation
        # 2. Return relevant snippets
        # For now, return a generic response
        return "Solana documentation suggests using the Anchor framework for smart contract development."

    def _construct_dev_prompt(self, question: str, context: str) -> str:
        """Construct a prompt for the LLM with context."""
        return f"""You are a Solana blockchain development expert. 
        Answer the following question using your knowledge and the provided context.
        
        Context from Solana documentation:
        {context}
        
        Question: {question}
        
        Please provide a clear and detailed answer with code examples if relevant."""

    def _generate_project_structure(self, name: str, framework: str) -> Dict[str, Any]:
        """Generate project structure based on framework."""
        if framework.lower() == "anchor":
            return {
                "type": "anchor",
                "directories": [
                    "programs/",
                    "tests/",
                    "app/",
                    "target/"
                ],
                "files": [
                    "Anchor.toml",
                    "package.json",
                    "programs/program-name/src/lib.rs",
                    "tests/program-name.ts",
                    "app/index.ts"
                ]
            }
        else:
            return {
                "type": "native",
                "directories": [
                    "src/",
                    "tests/",
                    "scripts/"
                ],
                "files": [
                    "package.json",
                    "tsconfig.json",
                    "src/index.ts",
                    "tests/index.test.ts"
                ]
            }

    def _generate_init_commands(self, name: str, framework: str) -> list:
        """Generate initialization commands for the project."""
        if framework.lower() == "anchor":
            return [
                f"anchor init {name}",
                "cd {name}",
                "anchor build",
                "anchor test"
            ]
        else:
            return [
                f"mkdir {name}",
                f"cd {name}",
                "npm init -y",
                "npm install --save @solana/web3.js"
            ]

    def _generate_code_template(self, template_type: str, **kwargs) -> str:
        """Generate code templates for different purposes."""
        if template_type == "program":
            return self.llm.generate_code(
                f"""Create a Solana program using Anchor with the following requirements:
                Program Name: {kwargs.get('name', 'MyProgram')}
                Description: {kwargs.get('description', 'A Solana program')}
                """,
                language="rust"
            )
        elif template_type == "client":
            return self.llm.generate_code(
                f"""Create a TypeScript client for interacting with a Solana program:
                Program ID: {kwargs.get('program_id', 'YOUR_PROGRAM_ID')}
                Functions: {kwargs.get('functions', ['initialize', 'process'])}
                """,
                language="typescript"
            )
        else:
            raise ValueError(f"Unknown template type: {template_type}")
