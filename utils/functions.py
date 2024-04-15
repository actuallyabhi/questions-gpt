from openai import OpenAI
from settings import OPENAI_API_KEY, OPENAI_ORGANIZATION

client = OpenAI(api_key=OPENAI_API_KEY,
                    organization=OPENAI_ORGANIZATION)


def upload_file(file_path):
    file = client.files.create(
        file=open(file_path, "rb"),
        purpose='assistants'
    )
    return file

def create_assistant(assistant_name,
                 	instruction,
                 	model="gpt-4-turbo"):
    
	assistant = client.beta.assistants.create(
        name = assistant_name,
        instructions = instruction,
        model=model,
        tools=[{"type": "retrieval"}]
        # file_ids=[uploaded_file.id]
	)
    
	return assistant

def update_assistant(assistant_id,file_id):
	assistant = client.beta.assistants.update(
		assistant_id=assistant_id,
		tools=[{"type": "retrieval"}],
		file_ids=[file_id]
	)
	return assistant

def initiate_interaction(user_message, uploaded_file):
    
	new_thread = client.beta.threads.create()
	message = client.beta.threads.messages.create(thread_id=new_thread.id,
                                              	role="user",
                                              	content=user_message,
                                              	file_ids=[uploaded_file]
	)
    
	return new_thread

def trigger_assistant(assistant_id, thread_id):
	run = client.beta.threads.runs.create_and_poll(
        thread_id = thread_id,
        assistant_id = assistant_id,		
	)
	if run.status == 'completed':
		messages = client.beta.threads.messages.list(
			thread_id=thread_id	
		)
	else:
		print(run.status)
	return messages

def generate_questions(prompt, file_id, assistant_id):
    try:
        new_thread = initiate_interaction(prompt, file_id)
        print(f"Thread ID: {new_thread.id}")
        messages = trigger_assistant(assistant_id, new_thread.id)
        response = messages.data[0].content[-1].text.value
        return response
    except Exception as e:
        raise e
	
def convert_to_json(data, prompt="""In the given text, Convert the text into valid json format. The JSON schema should be as follows: \n\n [ { \'mcq_id\': "1", \'question\': "<Question comes here>", "correct_option": "<1 or 2 or 3>", \'options\': [ { \'option_id\': "1", \'option_value\': "<Value of option 1>", }, { \'option_id\': "2", \'option_value\': "<Value of option 2>", }, { \'option_id\': "3", \'option_value\': "<Value of option 3>", } ], "explanation": "<Explain why was the correct answer correct, according to the book>", }, ... ]"""):
	response = client.chat.completions.create(
		model="gpt-4-turbo",
		messages=[
			{"role": "user", "content": prompt},
			{"role": "user", "content": data}
		],
		response_format={
			"type": "json_object"	
		},
		temperature=0
		
	)
	return response
	