from typing import Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from structured_models.input_tags import InputTagDescriptionList
from structured_models.input_tag_summary import InputTagSummaryList
from langchain_core.runnables import RunnableParallel
from multiprocessing import Process, Queue
import pprint


import os
from langchain_openai import ChatOpenAI


class LLMHandler:
    """Handles interactions with the LLM."""
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model_name=model_name)
    
    def evaluate_input_relevance(self,context_doc,input_tags):
        '''
            output example:

            is_relevant='yes' input_type='text' key='input_2' text_value='vineet.gandham@tamu.edu'
            is_relevant='yes' input_type='text' key='input_3' text_value='Vineet'
            is_relevant='yes' input_type='text' key='input_4' text_value='Gandham'
            is_relevant='yes' input_type='dropdown' key='input_5' text_value=None
            is_relevant='yes' input_type='text' key='input_6' text_value='(979)-344-3541'
            is_relevant='yes' input_type='dropdown' key='input_7' text_value=None
            is_relevant='yes' input_type='text' key='input_8' text_value=None
            is_relevant='yes' input_type='radiobutton' key='input_9' text_value=None
            is_relevant='no' input_type='radiobutton' key='input_10' text_value=None
            is_relevant='no' input_type='text' key='input_28' text_value=None
            is_relevant='yes' input_type='text' key='textarea_1' text_value='Note: i would need sponsorship.'
            is_relevant='no' input_type='text' key='textarea_2' text_value=None
        '''
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert extraction algorithm. "
                    "Only extract relevant information from the text. "
                    "If you do not know the value of an attribute asked to extract, "
                    "return null for the attribute's value.",
                ),
                ("human", " Here is the document you need to check relevancy from: {text}"),
                ("human", " Here are the html tags. The tags are ordered as we would see on a html based page to fill forms. So you can take help from surrounding tags to make a decision: {input_tags}"),
            ]
        )
        # Function to split data and process in parallel
        splitted_list_name = "input_tags"
        prompt_dict = {"text": context_doc,"input_tags": None}
        res = self._run_in_parallel(input_tags,prompt_template,splitted_list_name,InputTagDescriptionList,prompt_dict)
        print()
        pprint.pprint(res)
        return res
    
    def summarize_tags(self,input_tags):
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert in HTML semantics and input tag interpretation. Your task is to analyze HTML input tags and summarize their purpose and type into instances of the `InputTagSummary` class. Each input tag is represented as a dictionary containing its attributes, such as `id`, `type`, `class`, `aria-*` attributes, and surrounding metadata. Your goal is to determine the general input group and provide a short, descriptive summary of the tag’s purpose so that further relevant data can be input.",
                ),
                ("human", " Here are the html tags. The tags are ordered as we would see on a html based page to fill forms. So you can take help from surrounding tags to make a decision: {input_tags}"),
            ]
        )
        
        # Function to split data and process in parallel
        splitted_list_name = "input_tags"
        prompt_dict = {"input_tags": None}
        res = self._run_in_parallel(input_tags,prompt_template,splitted_list_name,InputTagSummaryList,prompt_dict)
        print()
        pprint.pprint(res)
        return res
    
    def select_drop_down(self,context_doc,desc,options):
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Select the specified option from the options which seem suitable given the context document. From that options, return ONLY one option as is in one line.",
                ),
                ("human", "Here is the context document : {context_doc}"),
                ("human", "Here is the question/description : {desc}"),
                ("human", "Here are the list of options : {options}"),
            ]
        )
        prompt = prompt_template.invoke({'context_doc':context_doc,'desc':desc,'options':options})
        res = self.llm.invoke(prompt)
        return res.content
    

    def choose_option(self,context_description,options,option_selection_directions):
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Select the specified option from the options which seem suitable given the context document. From that options, return ONLY one option as is in one line.",
                ),
                ("human", "Here is the context : {context_description}"),
                ("human", "Here are the list of options : {options} . {option_selection_directions}"),
            ]
        )
        prompt = prompt_template.invoke({'context_description':context_description,'options':options,'option_selection_directions':option_selection_directions})
        res = self.llm.invoke(prompt)
        return res.content
    
    
    def _run_in_parallel(self, result, prompt_template, splitted_list_name, schema,prompt_dict, num_processes=4):
        """
        Run processing in parallel using a configurable number of processes.

        Args:
            result (list): Input data to be processed.
            prompt_template: Prompt template for processing.
            splitted_list_name: Additional prompt-related data.
            schema: Schema for processing.
            num_processes (int): Number of parallel processes to use.

        Returns:
            list: Combined results from all processes.
        """
        # Split the result list into chunks
        num_processes = min(num_processes, len(result))
        chunk_size = len(result) // num_processes
        chunks = [result[i:i + chunk_size] for i in range(0, len(result), chunk_size)]

        # Handle edge case where result length is not divisible by num_processes
        if len(result) % num_processes != 0:
            chunks[-1].extend(result[num_processes * chunk_size:])

        # Queues to collect results from each process
        queues = [Queue() for _ in range(num_processes)]

        # Create and start processes
        processes = []
        for i in range(num_processes):
            process = Process(
                target=process_chunk,
                args=(chunks[i], prompt_template, splitted_list_name, schema, queues[i],prompt_dict, i + 1)
            )
            processes.append(process)
            process.start()

        # Wait for all processes to complete
        for process in processes:
            process.join()

        # Collect results from all queues
        results = [item for queue in queues for item in queue.get()]
        return results


    
    # Function to process a chunk of data using the LLM
def process_chunk(chunk,prompt_template,splitted_list_name,schema,queue,prompt_dict, chunk_id):
    llm = ChatOpenAI(model_name="gpt-4o-mini")
    structured_llm = llm.with_structured_output(schema=schema)
    results = []
    prompt = prompt_template.invoke({**prompt_dict,splitted_list_name:chunk})
    result = structured_llm.invoke(prompt)  # Synchronous call
    results.extend(result.tags)
    queue.put(results)