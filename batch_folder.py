from utils.functions import upload_file, convert_to_json, update_assistant, generate_questions
from utils.prompt import MCQ_prompt
import json
import csv
import os
from time import sleep
from random import randint

assistant_id = "asst_0IaOclIPn1lFGOgK0gfHkUiO"

if __name__ == "__main__":
    """
    This script is used to process a folder of PDF files.
    """
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        sys.exit("Please provide the path to the PDF file")

    if os.path.isdir(file_path):
        print(f"\nProcessing folder: {file_path}")
        for sub_filename in os.listdir(file_path):
            sub_file_path = os.path.join(file_path, sub_filename)
            if os.path.isfile(sub_file_path):
                print(f"\nProcessing file: {sub_file_path}")
                try:
                    csv_file_name = f"csv/{file_path.split('/')[-1]}.csv"
                    chapter_name = sub_filename.split(".")[0]
                    # log the chapter name
                    print(f"CSV File Name: {csv_file_name}")
                    print(f"Chapter Name: {chapter_name}")

                    if not os.path.exists(csv_file_name):
                        with open(csv_file_name, "w") as f:
                            writer = csv.writer(f)
                            writer.writerow(["chapter", "MCQ_Array"])

                    with open(csv_file_name, "a") as f:
                        writer = csv.writer(f)
                        file = upload_file(sub_file_path)
                        file_id = file.id

                        # generate all types of questions
                        update_assistant(assistant_id, file_id)
                        response = generate_questions(MCQ_prompt, file_id, assistant_id)
                        # TODO: Generate other types of questions
                        print(f"Intial Response: {response}")
                        try:
                            # if "Intial Response:" in response:
                            #    response = response.split("Intial Response:")[1]
                            #    key = list(formatted_response.keys())[0]
                            #    formatted_response = formatted_response[key]
                            # else:
                            response = response.replace(
                                "```json\n", "").replace("```", "")
                            formatted_response = json.loads(response)
                        except:
                            print("Error in occurred in parsing the response")
                            print("Converting the response to JSON")
                            response = convert_to_json(response)
                            formatted_response = json.loads(
                                response.choices[0].message.content)
                            if (type(formatted_response) == dict):
                                key = list(formatted_response.keys())[0]
                                formatted_response = formatted_response[key]
                            else:
                                formatted_response = formatted_response
                        writer.writerow([chapter_name, formatted_response])
                        sleep(randint(1, 5))
                except Exception as e:
                    print(e)
                    continue
            else:
                print(f"Folder contains a sub-folder: {sub_filename}")
                print("skiping the sub-folder")
                continue
    else:
        print("Please provide a valid folder path")
        sys.exit()
