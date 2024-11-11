# gpt_analyzer.py

import os
import openai
import requests
import json

class GPTAnalyzer:
    """Class for handling GPT analysis."""
    def __init__(self, config):
        self.api_key = config.openai_api_key
        if not self.api_key:
            raise Exception("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
        openai.api_key = self.api_key

    def analyze_friction_points(self, transcript_text):
        """Analyze friction points using GPT-4."""
        try:
            api_url = 'https://api.openai.com/v1/chat/completions'
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            prompt = self._create_prompt(transcript_text)
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that analyzes user interactions."},
                    {"role": "user", "content": prompt}
                ]
            }
            response = requests.post(api_url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")

    def _create_prompt(self, transcript_text):
        """Create prompt for GPT analysis."""
        return f"""
You are an expert in analyzing user interactions to identify friction points. A friction point is defined as any moment where the user encounters difficulties or inconveniences during an operation, such as confusion, frustration, delays, errors, or any form of discomfort.

I will provide you with a transcript of a user interaction, where each line includes a timestamp and the corresponding dialogue or event. Your task is to:

1. Identify all friction points: These could be moments where the user expresses confusion, encounters issues, asks for help, reports errors, or exhibits frustration.
2. For each friction point, provide:
   - The exact timestamp or time range where the friction point occurs.
   - A clear description of the friction point (e.g., what issue the user encountered, what caused the inconvenience).
   
Please return the analysis in the following structured format:
   
- **Friction Point #1**:
   - **Timestamp**: [start time] - [end time]
   - **Description**: [Clear description of the friction point]

- **Friction Point #2**:
   - **Timestamp**: [start time] - [end time]
   - **Description**: [Clear description of the friction point]

Here is the transcript:

{transcript_text}
"""
