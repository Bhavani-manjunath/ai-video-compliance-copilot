# AI Video Compliance Copilot

Team: Aivya

## Problem
Content creators often unknowingly violate copyright and trademark rules when producing videos.

## Solution
AI Video Compliance Copilot analyzes scripts and detects references to brands, fictional characters, music, and celebrities.

## AI Layer
The system uses Amazon Bedrock foundation models to perform script analysis and entity extraction.

## Architecture
User Script → FastAPI Backend → Amazon Bedrock → Risk Scoring Engine → Compliance Report
