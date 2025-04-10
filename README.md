# AIthentic
AI-powered authentication and verification system based on LLM agents

## Overview
AIthentic is a proof-of-concept system that leverages LLM agents for authentication and verification workflows. Built with agno framework, FastAPI, and Supabase.

## Environment Setup

### Prerequisites
- Python 3.12

### Setup Instructions

Choose one of the following methods to set up your virtual environment:

#### Option 1: Using venv (Recommended)
```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

#### Option 2: Using Conda
```bash
# Create and activate a conda environment
conda create -n AIthentic python=3.12
conda activate AIthentic

# Install dependencies
cd backend
pip install -r requirements.txt
```

#### Option 3: Using Pipenv
```bash
# Install pipenv if not already installed
pip install pipenv

# Create environment and install dependencies
cd backend
pipenv --python 3.12
pipenv install -r requirements.txt
pipenv shell
```

### Environment Configuration
Create a `.env` file in the `backend` directory with the following variables:

```bash
# Navigate to backend directory
cd backend

# Copy from example
cp .env.example .env

# Edit the .env file to add your API keys
```

Required variables in the `.env` file:
- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: (Optional) Your Supabase URL
- `SUPABASE_KEY`: (Optional) Your Supabase anon key
- `SUPABASE_SECRET`: (Optional) Your Supabase service role key

## Development Setup

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality. To set them up:

```bash
# Make sure you're in your virtual environment
# Install pre-commit
pip install pre-commit

# Navigate to backend directory
cd backend

# Install the git hooks
pre-commit install
```

This will automatically run code formatting and linting checks before each commit.

## Running the Application

```bash
# Make sure your virtual environment is activated

# Start the API server
cd backend
python -m uvicorn main:app --reload
```

The API server will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/api/docs`
- Health check: `http://localhost:8000/health`

## Project Structure

Detailed project planning and task lists are available in:
- `PLANNING.md`: Architecture and design decisions
- `TASK.md`: Current and completed tasks
