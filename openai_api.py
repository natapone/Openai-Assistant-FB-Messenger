from openai import OpenAI
import config
from utils import get_thread_id_from_recipient_id, update_thread_id_from_recipient_id

# Initialize the OpenAI client with the required default headers
client = OpenAI(
    api_key=config.OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

def ask_openai_assistant(query: str, recipient_id: str) -> str:
    try:
        # Retrieve or create a thread ID
        thread_id = get_thread_id_from_recipient_id(recipient_id)
        print(f"Retrieved thread ID: {thread_id}")

        if thread_id:
            thread = client.beta.threads.retrieve(thread_id=thread_id)
        else:
            thread = client.beta.threads.create()
            # Update the thread ID mapping
            update_thread_id_from_recipient_id(recipient_id, thread.id)

        print(f"Using thread ID: {thread.id}")

        # Create a message in the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            content=query,
            role="user"  # Specify user role
        )

        # Create a run for the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=config.ASSISTANT_ID
        )
        print(f"Run ID: {run.id}")

        # Poll until the run is completed
        while True:
            retrieved_run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if retrieved_run.status == "completed":
                break

        # Retrieve the messages in the thread
        retrieved_messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        print(f"First retrieved message: {retrieved_messages.data[0]}")

        # Extract the message text from the response
        message_text = retrieved_messages.data[0].content[0].text.value
        return message_text

    except Exception as e:
        # Log the exception details
        print(f"Error occurred: {e}")
        return config.ERROR_MESSAGE
