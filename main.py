import os
import csv
import sys
import openai
from prompts import ANALYZER_SYSTEM_PROMPT, GENERATOR_SYSTEM_PROMPT, ANALYZER_USER_PROMPT, GENERATOR_USER_PROMPT

# Prompt the user for OpenAI API key, API endpoint, and preferred model if not already set
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = input("Please enter your OpenAI API key: ")

if not os.getenv("OPENAI_API_ENDPOINT"):
    os.environ["OPENAI_API_ENDPOINT"] = input("Please enter your OpenAI API endpoint: ")

if not os.getenv("OPENAI_MODEL"):
    os.environ["OPENAI_MODEL"] = input("Please enter your preferred OpenAI Model (e.g., gpt-4, gpt-3.5-turbo): ")

# Set up the OpenAI API client
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_ENDPOINT")
openai_model = os.getenv("OPENAI_MODEL")

# Function to read the CSV file
def read_csv(file_path):
    data = []
    with open(file_path, "r", newline="") as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data.append(row)
    return data

# Function to save generated data to a new CSV file
def save_to_csv(data, output_file, headers=None):
    mode = 'w' if headers else 'a'
    with open(output_file, mode, newline="") as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
        for row in csv.reader(data.splitlines()):
            writer.writerow(row)

# Create the Analyzer Agent
def analyzer_agent(sample_data):
    response = openai.ChatCompletion.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": ANALYZER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": ANALYZER_USER_PROMPT.format(sample_data=sample_data)
            }
        ],
        max_tokens=400,
        temperature=0.1
    )
    return response.choices[0].message['content']

# Create the Generator Agent
def generator_agent(analysis_result, sample_data, num_rows=30):
    response = openai.ChatCompletion.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": GENERATOR_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": GENERATOR_USER_PROMPT.format(
                    num_rows=num_rows,
                    analysis_result=analysis_result,
                    sample_data=sample_data
                )
            }
        ],
        max_tokens=1500,
        temperature=1.0
    )
    return response.choices[0].message['content']

# Main execution flow
if __name__ == "__main__":
    # Check if the CSV file argument is provided
    if "--csv" in sys.argv and len(sys.argv) >= 3:
        file_path = sys.argv[2]  # Assume the CSV file argument is at index 2

        # Read the sample data from the input CSV file
        sample_data = read_csv(file_path)
        sample_data_str = "\n".join([",".join(row) for row in sample_data])

        print("\nLaunching team of Agents...")
        
        # Analyze the sample data using the Analyzer Agent
        analysis_result = analyzer_agent(sample_data_str)
        print("\n#### Analyzer Agent output: ####\n")
        print(analysis_result)
        print("\n--------------------------\n\nGenerating new data...")

        # Set up the output file
        output_file = "/app/new_dataset.csv"  # Modify as needed
        headers = sample_data[0] if sample_data else None

        # Create the output file with headers
        save_to_csv("", output_file, headers)

        batch_size = 30  # Number of rows to generate in each batch
        generated_rows = 0  # Counter to keep track of how many rows have been generated

        # Generate data in batches until we reach the desired number of rows
        while generated_rows < 100:  # Adjust as needed or use a different condition
            # Calculate how many rows to generate in this batch
            rows_to_generate = min(batch_size, 100 - generated_rows)  # Adjust the target rows here

            # Generate a batch of data using the Generator Agent
            generated_data = generator_agent(analysis_result, sample_data_str, rows_to_generate)

            # Append the generated data to the output file
            save_to_csv(generated_data, output_file)

            # Update the count of generated rows
            generated_rows += rows_to_generate

            # Print progress update
            print(f"Generated {generated_rows} rows out of 100")  # Adjust the total rows here

        # Inform the user that the process is complete
        print(f"Generated data has been saved to {output_file}")
    else:
        print("Error: Missing CSV file argument '--csv'")
        sys.exit(1)
