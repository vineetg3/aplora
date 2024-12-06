from socketio_instance import socketio
from llm import LLMHandler
from html_handler import HTMLHandler
from flask_socketio import emit, send
import pprint

class WorkflowRunner:
    """Coordinates the workflow pipeline."""
    def __init__(self, work_id, rendered_html):
        self.work_id = work_id
        self.rendered_html = rendered_html
        self.html_handler = None
        self.results = {}
        self.context = None
    
    def set_context_from_file(self, file_path: str) -> str:
        """
        Extracts and returns text content from a file.

        :param file_path: Path to the text file.
        :return: Extracted text content.
        :raises FileNotFoundError: If the file does not exist.
        :raises IOError: For other file read errors.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.context=file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at {file_path} was not found.")
        except IOError as e:
            raise IOError(f"An error occurred while reading the file: {e}")

    def run_step_1(self):
        tags = self.html_handler.tags_to_list()
        summarized_tags = LLMHandler().summarize_tags(tags)
        structured_input_tag_list = LLMHandler().evaluate_input_relevance(self.context,summarized_tags)
        # print(structured_input_tag_list)
        # structured_input_tag_list.tags.sort(key=lambda x: x.idx)
        def combine_tags_and_descriptions(html_tags, summarized_descriptions, input_descriptions):
            # Create lookup dictionaries for input_descriptions and summarized_descriptions using the `key` field
            
            description_lookup = {desc.key: desc for desc in input_descriptions}
            summary_description_lookup = {desc.key: desc for desc in summarized_descriptions}

            # Combine data
            combined = []
            for tag in html_tags:
                key = tag['key']
                # Initialize the combined entry with the base tag data
                combined_entry = tag.copy()

                # Add input description if available
                if key in description_lookup:
                    combined_entry.update(description_lookup[key].__dict__)

                # Add summarized description if available
                if key in summary_description_lookup:
                    combined_entry.update(summary_description_lookup[key].__dict__)

                combined.append(combined_entry)

            return combined

        tags = combine_tags_and_descriptions(tags,summarized_tags,structured_input_tag_list)
        return tags
    
    def _emit_fill_text_inputs(self, tags):
        """
        Handles emitting the 'fill_text_input' event for relevant text inputs.
        """
        autofill_texts = self._get_relevant_inputs_text(tags)
        for selector, value in autofill_texts:
            print("Fill text input: emitting,", selector, value)
            socketio.emit("fill_text_input", {"work_id": self.work_id, "selector": selector, "value": value})
    
    def _emit_fill_checkboxes(self, tags):
        """
        Handles emitting the 'fill_checkbox' event for relevant checkboxes.
        """
        autofill_checkbox = self._get_relevant_checkbox(tags)
        for selector in autofill_checkbox:
            print("Fill checkbox: emitting,", selector)
            socketio.emit("fill_checkbox", {"work_id": self.work_id, "selector": selector})
        
    def _emit_fill_radiobtns(self, tags):

        autofill_radiobtns = self._get_relevant_radiobtns(tags)
        for selector in autofill_radiobtns:
            print("Fill radio: emitting,", selector)
            socketio.emit("fill_radio_btn", {"work_id": self.work_id, "selector": selector})
    
    def _emit_fill_dropdowns(self,tags):
        for tag in tags:
            if (
                'dropdown' in str(tag.get('general_input_group', '') or '') and 
                'yes' in (tag.get('is_relevant_or_required', '') or '').lower() and
                (tag.get('is_filled', '') or '').lower() == 'no' and
                'select' not in str(tag.get('tag_type', '') or '')
            ):
                tag['is_filled']="yes"
                selector = self._css_selector(tag)
                print("Fill dropdown: emitting,", selector)
                socketio.emit('click_dropdown_and_select', {'work_id':self.work_id,'tag':tag})
    
    def _emit_fill_select_dropdown(self,tags):
        for tag in tags:
            general_input_group = tag.get('general_input_group', '')
            if (
                ('dropdown' in str(general_input_group or '') or 'select' in str(general_input_group or '')) and
                'yes' in (tag.get('is_relevant_or_required', '') or '').lower() and
                tag.get('select_option_value') is not None and
                (tag.get('is_filled', '') or '').lower() == 'no' and
                'select' in str(tag.get('tag_type', '') or '')
            ):
                option_value = LLMHandler().choose_option(tag.get('select_option_value'),tag.get('select_options'),"In the list of options, select the value which seems most likely.So if \"vaue\":\"Male\" is most likely, return Male.")
                tag['select_option_value'] = option_value
                tag['is_filled']="yes"
                selector = self._css_selector(tag)
                print("Fill dropdown: emitting,", tag)
                socketio.emit('select_option', {'work_id':self.work_id,'tag':tag})

    def run(self):
        self.html_handler = HTMLHandler(self.rendered_html)
        tags = self.run_step_1()
        pprint.pprint(tags)
        import json
        with open('output.json', 'w') as file:
            json.dump(tags, file, indent=4)


        self._emit_fill_dropdowns(tags)
        self._emit_fill_text_inputs(tags)
        with open('output.json', 'w') as file:
            json.dump(tags, file, indent=4)
        self._emit_fill_radiobtns(tags)
        self._emit_fill_checkboxes(tags)
        self._emit_fill_select_dropdown(tags)
        # tags = [dict1]
        

    def get_results(self):
        return self.results
    
    def _get_relevant_inputs_text(self,input_list):
            """
            Extracts a tuple of CSS selectors and text_value for relevant inputs.
            
            :param input_list: List of dictionaries representing inputs.
            :return: List of tuples (CSS selector, text_value).
            """
            results = []

            for item in input_list:
                # Check if the item meets the criteria
                if (
                    any('text' in str(item.get(field, '') or '')
                        for field in ['general_input_group', 'tag_type']) and
                    (item.get('is_relevant_or_required', '') or '').lower() == 'yes' and
                    item.get('text_value') is not None and
                    (item.get('is_filled', '') or '').lower() == 'no'
                ):
                    results.append((self._css_selector(item),item.get('text_value')))
                    item["is_filled"] = "yes"
            return results
    
    def _get_relevant_checkbox(self,input_list):
            """
            Extracts a tuple of CSS selectors and text_value for relevant inputs.
            
            :param input_list: List of dictionaries representing inputs.
            :return: List of tuples (CSS selector, text_value).
            """
            results = []

            for item in input_list:
                # Check if the item meets the criteria
                if (
                    ('check' in str(item.get('general_input_group', '') or '')) and 
                    (item.get('is_relevant_or_required') or '').lower() == 'yes' and
                    (item.get('is_filled') or '').lower() == 'no'
                ):
                    results.append(self._css_selector(item))
                    item["is_filled"] = "yes"
            return results
    
    def _get_relevant_radiobtns(self,input_list):
            results = []

            for item in input_list:
                # Check if the item meets the criteria
                if (
                    (
                        ('radio' in str(item.get('general_input_group', '') or '')) or 
                        ('radio' in str(item.get('tag_type', '') or ''))
                    ) and 
                    str(item.get('is_relevant_or_required', '') or '').lower() == 'yes'
                ):
                    results.append(self._css_selector(item))
                    item["is_filled"] = "yes"
            return results

    def _css_selector(self,tag):
        tag_type = tag.get('tag_type', 'input')
        selector_parts = [tag_type]

        # Add allowed attributes to the selector
        for attr in HTMLHandler.allowed_attrs:
            if attr in tag and tag[attr] is not None:
                attr_value = tag[attr]
                
                # If the attribute value is a list, join it into a single string
                if isinstance(attr_value, list):
                    attr_value = ' '.join(attr_value)  # You can change the separator if needed
                
                # Append the attribute to the selector
                selector_parts.append(f'[{attr}="{attr_value}"]')
        
        # Join parts to form the full selector
        css_selector = ''.join(selector_parts)
        return css_selector

dict1 = {
    'class': ['select__input'],
    'id': 'question_11338566004',
    'aria-describedby': 'question_11338566004-error',
    'aria-haspopup': 'true',
    'aria-required': 'false',
    'autocomplete': 'off',
    'type': 'text',
    'value': '',
    'text_above_htmltag': ['Other Website', 'Pronouns', 'they/them/theirs'],
    'text_below_htmltag': ["If you'd like to, please let us know your pronouns.", 'Are you authorized to work in the country for which you applied?', '*'],
    'key': 'input_15',
    'idx': 24,
    'tag_type': 'input',
    'is_relevant_or_required': 'yes',
    'text_value': 'He/him',
    'is_filled': 'no',
    'general_input_group': 'dropdown',
    'description': 'A dropdown selection for the user to choose an option related to their pronouns.'
}

# dict2 = {
#     'class': ['select__input'],
#     'id': 'question_11338570004',
#     'aria-describedby': 'react-select-question_11338570004-placeholder question_11338570004-error',
#     'aria-haspopup': 'true',
#     'aria-required': 'true',
#     'autocomplete': 'off',
#     'type': 'text',
#     'value': '',
#     'text_above_htmltag': ['Are you authorized to work in the country for which you applied?', '*', 'Select...'],
#     'text_below_htmltag': ['Have you ever worked for Figma before, as an employee or a contractor/consultant?', '*', 'Select...'],
#     'key': 'input_16',
#     'idx': 27,
#     'tag_type': 'input',
#     'is_relevant_or_required': 'yes',
#     'text_value': None,
#     'is_filled': 'no',
#     'general_input_group': 'dropdown',
#     'description': 'A required dropdown for the user to select if they are authorized to work in the country.'
# }

# dict3 = {
#     'class': ['select__input'],
#     'id': 'question_11338571004',
#     'aria-describedby': 'react-select-question_11338571004-placeholder question_11338571004-error',
#     'aria-haspopup': 'true',
#     'aria-required': 'true',
#     'autocomplete': 'off',
#     'type': 'text',
#     'value': '',
#     'text_above_htmltag': ['Have you ever worked for Figma before, as an employee or a contractor/consultant?', '*', 'Select...'],
#     'text_below_htmltag': ['Voluntary Self-Identification', 'For government reporting purposes, we ask candidates to respond to the below self-identification survey.\nCompletion of t'],
#     'key': 'input_18',
#     'idx': 30,
#     'tag_type': 'input',
#     'is_relevant_or_required': 'yes',
#     'text_value': None,
#     'is_filled': 'no',
#     'general_input_group': 'dropdown',
#     'description': 'A required dropdown for the user to select prior employment status with Figma.'
# }